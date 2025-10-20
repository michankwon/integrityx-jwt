export interface FileData {
  fileInfo: {
    file: {
      UID: string | null;
      size: number;
      Status: string;
      FH: string;
    };
    fileSignature: string;
    fileHash: string;
    totalEncryptedChunkFile: number;
  };
}

export interface FileVerificationResponse {
  success: boolean;
  message: string;
  data: {
    fileInfo: {
      file: {
        UID: string | null;
        size: number;
        Status: string;
        FH: string;
      };
      fileSignature: string;
      fileHash: string;
      totalEncryptedChunkFile: number;
    };
  };
}

type FieldType = {
  FieldName: string;
  DataType: string;
  MaxLength?: number;
  Required?: boolean;
  Default?: any;
};

type IndexType = {
  Fields: string[];
  IndexValue: string;
  ForceUpdate: boolean;
  Delete: boolean;
};

export interface SchemaType {
  ETId: number;
  TableName: string;
  Family: string;
  DoSummary: boolean;
  Fields: FieldType[];
  Indexes: IndexType[];
}

import { RoleData } from "@/schemas/roleSchema";
import { ProfileData } from "@/schemas/profileSchema";
import { BlogData } from "@/schemas/blogSchema";

export type MainData = BlogData | ProfileData | RoleData;
export type SchemaData = BlogData[] | ProfileData[] | RoleData[];
