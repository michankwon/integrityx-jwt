import { SchemaType } from "@/types/schema";

export const roleSchema: SchemaType = {
  ETId: Number(process.env.NEXT_PUBLIC_WALACOR_ROLE_ETID),
  TableName: "roles",
  Family: "role-family",
  DoSummary: true,
  Fields: [
    {
      FieldName: "id",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "roleName",
      DataType: "TEXT",
      MaxLength: 255,
      Required: false,
    },
    {
      FieldName: "scope",
      DataType: "TEXT",
      MaxLength: 255,
      Required: false,
    },
  ],
  Indexes: [
    {
      Fields: ["id"],
      IndexValue: "id",
      ForceUpdate: false,
      Delete: false,
    },
    {
      Fields: ["roleName"],
      IndexValue: "roleName",
      ForceUpdate: false,
      Delete: false,
    },
  ],
};

export interface RoleData {
  UID?: string;
  id: string;
  roleName: string;
  scope: string;
  selectedVersion?: boolean;
}
