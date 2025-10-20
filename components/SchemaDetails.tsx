import React, { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronDown, faChevronUp } from "@fortawesome/free-solid-svg-icons";
import Button from "./single/Button";
import { useCreateSchema } from "@/hooks/schema/useCreateSchema";
import { toast } from "react-hot-toast";
import { successToastStyle, errorToastStyle, loadingToastStyle } from "@/styles/toastStyles";

interface FieldType {
  FieldName: string;
  DataType: string;
  MaxLength?: number;
  Required?: boolean;
  Default?: any;
}

interface SchemaType {
  ETId: number;
  TableName: string;
  Family: string;
  DoSummary: boolean;
  Fields: FieldType[];
}

interface SchemaDetailsProps {
  schema: SchemaType;
  name: string;
}

const SchemaDetails: React.FC<SchemaDetailsProps> = ({ schema, name }) => {
  const { createSchema } = useCreateSchema();
  const [isFieldsOpen, setIsFieldsOpen] = useState(false);

  const toggleFields = () => setIsFieldsOpen((prev) => !prev);

  const visibleFields = isFieldsOpen ? schema.Fields : schema.Fields.slice(0, 3);

  async function handleCreateSchema(etid: number) {
    toast.loading("Creating schema...", loadingToastStyle);

    try {
      await createSchema(etid, schema);
      toast.dismiss();
      toast.success("Schema created successfully!", successToastStyle);
    } catch (error) {
      toast.dismiss();
      toast.error("Failed to create schema.", errorToastStyle);
      console.error("Error creating schema:", error);
    }
  }

  return (
    <div className="bg-white p-6 mb-8 w-full shadow-lg rounded-lg">
      <h2 className="text-2xl font-semibold mb-4">{name} Schema</h2>

      <div className="bg-gray-50 p-4 rounded-lg mb-6">
        <p className="text-gray-800 mb-2">
          <strong>Table Name:</strong> {schema.TableName}
        </p>
        <p className="text-gray-800 mb-2">
          <strong>ETId (Envelope Type ID):</strong> {schema.ETId}
        </p>
        <p className="text-gray-800 mb-2">
          <strong>Family:</strong> {schema.Family}
        </p>
        <p className="text-gray-800 mb-2">
          <strong>Summary Enabled:</strong> {schema.DoSummary ? "Yes" : "No"}
        </p>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-4">Understanding Table Name, Family, and ETId</h3>
        <p className="text-gray-700 mb-4">
          <strong>Table Name</strong> uniquely identifies the schema within the database. For example, you might have separate schemas for &quot;Blog Posts&quot; and &quot;Blog Images&quot; but group them under the same family for better
          organization.
        </p>
        <p className="text-gray-700 mb-4">
          The <strong>Family</strong> property groups related schemas together. For instance, all schemas related to blogs could be grouped under the &quot;Blog&quot; family.
        </p>
        <p className="text-gray-700 mb-4">
          <strong>ETId (Envelope Type ID)</strong> is a unique identifier used by Walacor to validate and communicate with your schema. It works like an &quot;envelope&quot; that wraps your data to ensure it matches the schema before
          processing.
        </p>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg mb-6 relative cursor-pointer hover:bg-gray-100 transition-all" onClick={toggleFields}>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">Fields</h3>
          <button className="text-gray-700 focus:outline-none" onClick={toggleFields} aria-expanded={isFieldsOpen}>
            <FontAwesomeIcon icon={isFieldsOpen ? faChevronUp : faChevronDown} />
          </button>
        </div>
        <ul className="list-none text-gray-700">
          {visibleFields.map((field, index) => (
            <li key={index} className="bg-gray-100 mb-2 p-3 rounded-lg">
              <p>
                <strong>{field.FieldName}</strong> - {field.DataType}
                {field.MaxLength && ` (Max Length: ${field.MaxLength})`}
                {field.Required && ` (Required)`}
                {field.Default !== undefined && ` (Default: ${field.Default})`}
              </p>
            </li>
          ))}
        </ul>
        {!isFieldsOpen && schema.Fields.length > 3 && <p className="text-gray-500">+ {schema.Fields.length - 3} more fields</p>}
        {schema.Fields.length > 3 && <div className={`absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-gray-50 to-transparent ${isFieldsOpen ? "opacity-100" : "opacity-0"}`} />}
      </div>

      <Button onClick={() => handleCreateSchema(schema.ETId)} className="w-full bg-primary text-primary-foreground">
        Create Schema
      </Button>
    </div>
  );
};

export default SchemaDetails;
