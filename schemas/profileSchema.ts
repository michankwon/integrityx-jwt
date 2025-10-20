import { SchemaType } from "@/types/schema";

export const profileSchema: SchemaType = {
  ETId: Number(process.env.NEXT_PUBLIC_WALACOR_PROFILE_ETID),
  TableName: "profile",
  Family: "profile-family",
  DoSummary: true,
  Fields: [
    {
      FieldName: "id",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "userId",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "firstName",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "lastName",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "userRole",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "isConfigured",
      DataType: "BOOLEAN",
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
      Fields: ["userRole"],
      IndexValue: "userRole",
      ForceUpdate: false,
      Delete: false,
    },
  ],
};

export interface ProfileData {
  UID?: string;
  id?: string;
  userId?: string;
  firstName?: string;
  lastName?: string;
  IsDeleted?: boolean;
  userRole?: string;
  isConfigured?: boolean;
  CreatedAt?: number;
  selectedVersion?: boolean;
}
