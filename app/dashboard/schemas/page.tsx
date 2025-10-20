"use client";

import React, { useState, useEffect } from "react";
import DashboardLayout from "@/layout/dashboard.layout";
import SchemaDetails from "@/components/SchemaDetails";
import { blogSchema } from "@/schemas/blogSchema";
import Button from "@/components/single/Button";
import { profileSchema } from "@/schemas/profileSchema";
import { roleSchema } from "@/schemas/roleSchema";
import SubDashboardLayout from "@/layout/subdashboard.layout";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCode, faDatabase, faUser } from "@fortawesome/free-solid-svg-icons";

type SchemaObject = {
  schema: typeof blogSchema | typeof profileSchema | typeof roleSchema;
  name: string;
};

export const schemas: SchemaObject[] = [
  { schema: blogSchema, name: "Blog" },
  { schema: profileSchema, name: "Profile" },
  { schema: roleSchema, name: "Role" },
];

const SchemasPage = () => {
  const [selectedTab, setSelectedTab] = useState("about");
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return null;
  }

  return (
    <DashboardLayout>
      <SubDashboardLayout>
        <div className="container mx-auto py-6 md:py-12 px-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl md:text-4xl font-semibold mb-4 md:mb-6 text-center">Schemas</h1>
          <p className="text-gray-600 mb-4 md:mb-6 text-center text-sm md:text-base">Schemas define the structure of your data and ensure consistency.</p>

          <div className="flex flex-wrap justify-center items-center mb-6 md:mb-8 gap-2 md:gap-4">
            <Button onClick={() => setSelectedTab("about")} className={`px-3 py-1 md:px-4 md:py-2 text-white text-sm md:text-base ${selectedTab === "about" ? "bg-primary" : "bg-gray-400 hover:bg-gray-500"}`}>
              About
            </Button>
            {schemas.map((schemaObj, index) => (
              <Button key={index} onClick={() => setSelectedTab(schemaObj.name)} className={`px-3 py-1 md:px-4 md:py-2 text-white text-sm md:text-base ${selectedTab === schemaObj.name ? "bg-primary" : "bg-gray-400 hover:bg-gray-500"}`}>
                {schemaObj.name}
              </Button>
            ))}
          </div>

          {selectedTab === "about" ? (
            <div className="bg-white p-4 md:p-6 rounded-lg shadow-lg mb-6 max-w-full md:max-w-2xl mx-auto">
              <h2 className="text-xl md:text-2xl font-semibold mb-4">Understanding Schemas</h2>
              <p className="text-gray-700 mb-4 text-sm md:text-base">
                In Walacor, a <strong>schema</strong> defines the structure of your data. It includes fields that specify the data type, length, and whether the field is required. These schemas ensure consistency and integrity when saving
                your data.
              </p>
              <p className="text-gray-700 mb-4 text-sm md:text-base">
                For example, when you submit a blog or profile, the schema validates the data before saving it to the Walacor platform. This process guarantees that the data is structured correctly and maintains a high level of integrity.
              </p>

              <div className="flex flex-col items-center justify-center mb-4">
                <div className="flex flex-col md:flex-row items-center w-full justify-between text-sm md:text-base text-center md:text-left">
                  <strong>Data Flow in Walacor:</strong>
                  <div className="flex items-center gap-1 my-2">
                    <FontAwesomeIcon icon={faUser} className="mr-1" /> <strong>Payload</strong> →
                    <FontAwesomeIcon icon={faCode} className="mx-1" /> <strong>Schemas</strong> →
                    <FontAwesomeIcon icon={faDatabase} className="mx-1" /> <strong>Walacor</strong>
                  </div>
                </div>
              </div>

              <p className="text-gray-700 mb-4 text-sm md:text-base">
                A <strong>payload</strong> is the actual data sent to the server, such as user input or form data. Before this data is stored, it&apos;s validated against the defined schema to ensure that it meets all the requirements.
              </p>

              <h3 className="text-lg md:text-xl font-semibold mt-6 mb-4">To-Do Schema Example</h3>
              <p className="text-gray-700 mb-4 text-sm md:text-base">A simple example of a schema for a &quot;To Do&quot; item might look like this:</p>
              <pre className="bg-gray-100 p-3 md:p-4 rounded mb-6 text-xs md:text-sm text-left overflow-x-auto whitespace-pre-wrap">
                {`{
  id: "text",
  text: "string",
  isCompleted: "boolean"
}`}
              </pre>

              <h3 className="text-lg md:text-xl font-semibold mt-6 mb-4">To-Do Payload Examples</h3>
              <p className="text-gray-700 mb-4 text-sm md:text-base">Here are a few example payloads for the above &quot;To Do&quot; schema:</p>
              <pre className="bg-gray-100 p-3 md:p-4 rounded mb-6 text-xs md:text-sm text-left overflow-x-auto whitespace-pre-wrap">
                {`[
  { id: "1", text: "Buy groceries", isCompleted: false },
  { id: "2", text: "Walk the dog", isCompleted: true },
  { id: "3", text: "Finish coding project", isCompleted: false }
]`}
              </pre>

              <p className="text-gray-700 mb-4 text-sm md:text-base">
                As you can see, the payloads must match the schema. Each to-do item has an <strong>id</strong>, <strong>text</strong> to describe the task, and a <strong>isCompleted</strong> field to track if it&apos;s done.
              </p>

              <h3 className="text-lg md:text-xl font-semibold mt-6 mb-4">Your Experience After Schemas Are Generated</h3>
              <p className="text-gray-700 mb-4 text-sm md:text-base">
                Once schemas are generated, the user experience becomes seamless. Every time you submit data, like a &quot;To Do&quot; item, the platform automatically checks the payload against the schema to ensure that your data is
                structured correctly. This process ensures that your data remains high-quality and consistent across all interactions.
              </p>

              <div className="flex flex-col items-center justify-center mb-4">
                <div className="flex flex-col md:flex-row items-center w-full justify-between text-sm md:text-base text-center md:text-left">
                  <strong>Your experience after schemas are generated follows:</strong>
                  <div className="flex items-center gap-1 my-2">
                    <FontAwesomeIcon icon={faUser} className="mr-1" /> <strong>Payload</strong> →
                    <FontAwesomeIcon icon={faDatabase} className="mx-1" /> <strong>Walacor</strong>
                  </div>
                </div>
              </div>

              <h3 className="text-lg md:text-xl font-semibold mt-6 mb-4">The Value of Validated and Quality Data</h3>
              <p className="text-gray-700 mb-4 text-sm md:text-base">
                On the other side of the equation, the company or individual using the Walacor platform benefits from validated and consistent data. Since all payloads must conform to the predefined schemas, this ensures that the data being
                stored is of high quality. For companies, this results in more reliable data insights, fewer errors, and easier data management.
              </p>
            </div>
          ) : (
            <SchemaDetails schema={schemas.find((schemaObj) => schemaObj.name === selectedTab)!.schema} name={selectedTab} />
          )}
        </div>
      </SubDashboardLayout>
    </DashboardLayout>
  );
};

export default SchemasPage;
