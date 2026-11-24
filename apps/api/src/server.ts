import express, { type Request, type Response } from "express";
import { randomUUID } from "node:crypto";
import { generateWeeklyReport } from "./jobs/generateWeeklyReport.ts";

interface ServerOptions {
  reportDirectory?: string;
}

export function createServer(options: ServerOptions = {}) {
  const app = express();
  const runs: Array<{
    id: string;
    triggerType: "manual";
    status: "success" | "failed";
    startedAt: string;
    endedAt: string;
    reportId?: string;
    reportPath?: string;
    safeErrorCategory?: string;
    safeErrorSummary?: string;
  }> = [];

  app.use((request, response, next) => {
    const remoteAddress = (request.ip ?? "").replace("::ffff:", "");
    if (!["127.0.0.1", "::1"].includes(remoteAddress)) {
      response.status(403).json({
        error: { code: "FORBIDDEN_HOST", message: "Loopback access required" },
      });
      return;
    }
    response.setHeader("Access-Control-Allow-Origin", "http://127.0.0.1:5173");
    response.setHeader("Access-Control-Allow-Headers", "Content-Type");
    if (request.method === "OPTIONS") {
      response.sendStatus(204);
      return;
    }
    next();
  });
  app.use(express.json());

  app.get("/health", (_request: Request, response: Response) => {
    response.status(200).json({ status: "ok" });
  });

  app.get("/api/configuration/status", (_request: Request, response: Response) => {
    response.status(200).json({
      status: "blocked",
      jira: {
        connected: false,
        projectKey: null,
        boardId: null,
      },
    });
  });

  app.get("/api/runs", (_request: Request, response: Response) => {
    response.status(200).json({
      data: runs.slice(0, 25),
      meta: { limit: 25, hasMore: runs.length > 25 },
    });
  });

  app.post("/api/runs", async (_request: Request, response: Response) => {
    const runId = randomUUID();
    const startedAt = new Date();

    try {
      const report = await generateWeeklyReport({
        reportDirectory: options.reportDirectory,
        generatedAt: startedAt,
      });
      const endedAt = new Date();
      const run = {
        id: runId,
        triggerType: "manual" as const,
        status: "success" as const,
        startedAt: startedAt.toISOString(),
        endedAt: endedAt.toISOString(),
        reportId: report.id,
        reportPath: report.canonicalPath,
      };
      runs.unshift(run);

      response.status(201).json({ data: { run, report } });
    } catch (error) {
      const endedAt = new Date();
      const summary =
        error instanceof Error
          ? error.message
          : "Unknown report generation error";
      console.error("Mock report generation failed:", summary);
      runs.unshift({
        id: runId,
        triggerType: "manual",
        status: "failed",
        startedAt: startedAt.toISOString(),
        endedAt: endedAt.toISOString(),
        safeErrorCategory: "REPORT_GENERATION_FAILED",
        safeErrorSummary: "The demonstration report could not be written.",
      });

      response.status(500).json({
        error: {
          code: "REPORT_GENERATION_FAILED",
          message: "The demonstration report could not be generated.",
        },
      });
    }
  });

  app.use((_request: Request, response: Response) => {
    response.status(404).json({ error: { code: "NOT_FOUND", message: "Not found" } });
  });

  return app;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const port = Number(process.env.PORT ?? 3001);
  const app = createServer();
  app.listen(port, "127.0.0.1", () => {
    console.log(`API listening on http://127.0.0.1:${port}`);
  });
}