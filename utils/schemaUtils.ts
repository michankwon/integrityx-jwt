import { blogSchema } from "@/schemas/blogSchema";
import { profileSchema } from "@/schemas/profileSchema";
import { roleSchema } from "@/schemas/roleSchema";

export const createSchemas = async (createSchema: Function) => {
  const schemas = [
    { etid: profileSchema.ETId, schemaData: profileSchema },
    { etid: blogSchema.ETId, schemaData: blogSchema },
    { etid: roleSchema.ETId, schemaData: roleSchema },
  ];

  for (const schema of schemas) {
    await createSchema(schema.etid, schema.schemaData);
  }
};
