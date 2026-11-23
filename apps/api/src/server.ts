import express, { type Request, type Response } from "express";

export function createServer() {
  const app = express();
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
    response.status(200).json({ data: [], meta: { limit: 25, hasMore: false } });
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