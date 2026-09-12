export type Operation = "diagnose" | "format" | "minify" | "repair" | "schema_validate";
export type PayloadType = "generic" | "api_gateway" | "sqs" | "sns" | "eventbridge";

export interface Issue {
  code: string;
  path?: string;
  message: string;
  expected?: unknown;
  received?: unknown;
  hint?: string;
}

export interface Metrics {
  bytes: number;
  depth: number;
  keys: number;
  arrays: number;
  values: number;
}

export interface RepairChange {
  type: string;
  message: string;
  line: number;
}

export interface AnalyzeResult {
  success: boolean;
  operation?: Operation;
  payloadType?: PayloadType;
  jsonValid?: boolean;
  structureValid?: boolean;
  schemaValid?: boolean;
  schemaAccepted?: boolean;
  repaired?: boolean;
  message?: string;
  errors?: Issue[];
  warnings?: Issue[];
  metrics?: Metrics;
  output?: string | null;
  sizes?: {
    originalBytes: number;
    formattedBytes?: number;
    minifiedBytes?: number;
    bytesSaved?: number;
    percentageReduction?: number;
  };
  changes?: RepairChange[];
  error?: Issue & { line?: number; column?: number; position?: number; reason?: string; excerpt?: string };
}

export interface AnalyzeRequest {
  operation: Operation;
  payloadType: PayloadType;
  content: string;
  schema: string | null;
}
