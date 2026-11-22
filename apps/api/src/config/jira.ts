export interface JiraConnectionConfig {
  siteUrl: string | null;
  siteUrlConfirmed: boolean;
  projectKey: string | null;
  projectKeyConfirmed: boolean;
  boardId: number | null;
  activeSprintConfirmed: boolean;
}

export type JiraConnectionValidation =
  | {
      status: "configured";
      config: JiraConnectionConfig;
      errors: [];
    }
  | {
      status: "blocked";
      config: JiraConnectionConfig;
      errors: string[];
    };

function isPlaceholderUrl(value: string): boolean {
  const normalized = value.toLowerCase();
  return (
    normalized.includes("company.atlassian.net") ||
    normalized.includes("example") ||
    normalized.includes("placeholder")
  );
}

export function validateJiraConnectionConfig(
  config: JiraConnectionConfig,
): JiraConnectionValidation {
  const errors: string[] = [];

  if (!config.siteUrlConfirmed) {
    errors.push("Jira Cloud site URL is not confirmed.");
  } else if (!config.siteUrl) {
    errors.push("Jira Cloud site URL is missing.");
  } else {
    try {
      const url = new URL(config.siteUrl);
      if (
        url.protocol !== "https:" ||
        !url.hostname ||
        isPlaceholderUrl(url.hostname)
      ) {
        errors.push("Jira Cloud site URL must be an approved HTTPS URL.");
      }
    } catch {
      errors.push("Jira Cloud site URL is invalid.");
    }
  }

  if (!config.projectKeyConfirmed) {
    errors.push("Jira project key is not confirmed.");
  } else if (
    !config.projectKey ||
    !/^[A-Z][A-Z0-9]*$/.test(config.projectKey)
  ) {
    errors.push("Jira project key is missing or invalid.");
  }

  if (
    config.boardId === null ||
    !Number.isInteger(config.boardId) ||
    config.boardId <= 0
  ) {
    errors.push("Jira board ID must be a positive integer.");
  }

  if (!config.activeSprintConfirmed) {
    errors.push("The board's active-sprint behavior is not confirmed.");
  }

  if (errors.length > 0) {
    return { status: "blocked", config, errors };
  }

  return { status: "configured", config, errors: [] };
}
