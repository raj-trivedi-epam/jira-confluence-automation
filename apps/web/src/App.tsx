export default function App() {
  const runHealthCheck = async () => {
    await fetch("http://127.0.0.1:3001/health");
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        fontFamily: "system-ui, sans-serif",
        background: "#f6f7f9",
        color: "#172b4d",
      }}
    >
      <section
        style={{
          width: "min(680px, calc(100vw - 48px))",
          padding: "32px",
          border: "1px solid #dfe1e6",
          borderRadius: "12px",
          background: "#fff",
          boxShadow: "0 8px 24px rgba(9, 30, 66, 0.08)",
        }}
      >
        <p style={{ margin: 0, color: "#505f79", fontWeight: 600 }}>
          Prototype
        </p>
        <h1 style={{ marginBottom: "8px" }}>Jira/Confluence Automation</h1>
        <p style={{ color: "#505f79" }}>
          React 18 frontend is running on loopback.
        </p>
        <button
          type="button"
          onClick={runHealthCheck}
          style={{
            border: 0,
            borderRadius: "6px",
            padding: "10px 14px",
            background: "#dfe1e6",
            color: "#172b4d",
            fontWeight: 600,
          }}
        >
          Generate report
        </button>
      </section>
    </main>
  );
}