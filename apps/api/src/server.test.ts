import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { test } from "node:test";
import { createServer } from "./server.ts";

async function startServer(reportDirectory: string) {
  const app = createServer({ reportDirectory });
  const server = app.listen(0, "127.0.0.1");

  await new Promise<void>((resolve, reject) => {
    server.once("listening", resolve);
    server.once("error", reject);
  });

  const address = server.address();
  if (!address || typeof address === "string") {
    await new Promise<void>((resolve) => server.close(() => resolve()));
    throw new Error("The test server did not bind to a TCP port.");
  }
  const port = address.port;

  return {
    url: `http://127.0.0.1:${port}`,
    close: () =>
      new Promise<void>((resolve, reject) => {
        server.close((error) => (error ? reject(error) : resolve()));
      }),
  };
}

test("manual generation writes and returns a mock report and records the run", async () => {
  const temporaryDirectory = await mkdtemp(
    path.join(tmpdir(), "jira-report-test-"),
  );
  const reportDirectory = path.join(temporaryDirectory, "reports");
  const server = await startServer(reportDirectory);

  try {
    const response = await fetch(`${server.url}/api/runs`, { method: "POST" });
    assert.equal(response.status, 201);

    const result = (await response.json()) as {
      data: {
        run: { id: string; status: string; reportPath: string };
        report: { id: string; canonicalPath: string; content: string };
      };
    };

    assert.equal(result.data.run.status, "success");
    assert.equal(
      result.data.run.reportPath,
      result.data.report.canonicalPath,
    );
    assert.match(result.data.report.content, /DEMO DATA ONLY/);
    assert.match(result.data.report.content, /## Executive Summary/);
    assert.match(result.data.report.content, /## Delivery Update/);
    assert.match(result.data.report.content, /## Sprint Progress/);
    assert.match(result.data.report.content, /## Blockers and Risks/);
    assert.match(
      result.data.report.content,
      /## Decisions or Support Needed/,
    );
    assert.match(result.data.report.content, /## Data Notes/);
    assert.equal(
      await readFile(result.data.report.canonicalPath, "utf8"),
      result.data.report.content,
    );

    const historyResponse = await fetch(`${server.url}/api/runs`);
    const history = (await historyResponse.json()) as {
      data: Array<{ id: string; status: string }>;
    };
    assert.equal(history.data.length, 1);
    assert.equal(history.data[0].id, result.data.run.id);
    assert.equal(history.data[0].status, "success");

    const secondResponse = await fetch(`${server.url}/api/runs`, {
      method: "POST",
    });
    const secondResult = (await secondResponse.json()) as {
      data: { report: { canonicalPath: string } };
    };
    assert.equal(secondResponse.status, 201);
    assert.match(secondResult.data.report.canonicalPath, /-r02\.md$/);
  } finally {
    await server.close();
    await rm(temporaryDirectory, { recursive: true, force: true });
  }
});

test("manual generation failures return an error and record the failed run", async () => {
  const temporaryDirectory = await mkdtemp(
    path.join(tmpdir(), "jira-report-test-"),
  );
  const reportDirectory = path.join(temporaryDirectory, "not-a-directory");
  await writeFile(reportDirectory, "block report output");
  const server = await startServer(reportDirectory);

  try {
    const response = await fetch(`${server.url}/api/runs`, { method: "POST" });
    assert.equal(response.status, 500);
    assert.deepEqual(await response.json(), {
      error: {
        code: "REPORT_GENERATION_FAILED",
        message: "The demonstration report could not be generated.",
      },
    });

    const historyResponse = await fetch(`${server.url}/api/runs`);
    const history = (await historyResponse.json()) as {
      data: Array<{
        status: string;
        safeErrorCategory: string;
        safeErrorSummary: string;
      }>;
    };
    assert.equal(history.data[0].status, "failed");
    assert.equal(
      history.data[0].safeErrorCategory,
      "REPORT_GENERATION_FAILED",
    );
    assert.equal(
      history.data[0].safeErrorSummary,
      "The demonstration report could not be written.",
    );
  } finally {
    await server.close();
    await rm(temporaryDirectory, { recursive: true, force: true });
  }
});
