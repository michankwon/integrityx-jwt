import { useEffect, useState } from "react";
import { useCreateSchema } from "@/hooks/schema/useCreateSchema";
import { useReadSchemas } from "@/hooks/schema/useReadSchemas";
import { blogSchema } from "@/schemas/blogSchema";
import { profileSchema } from "@/schemas/profileSchema";
import { roleSchema } from "@/schemas/roleSchema";

export const useInitializeSchemas = () => {
  const { createSchema, loading: creatingSchema } = useCreateSchema();

  const { data: profileData, readSchemas: readProfileSchemas } = useReadSchemas(profileSchema.ETId);
  const { data: blogData, readSchemas: readBlogSchemas } = useReadSchemas(blogSchema.ETId);
  const { data: roleData, readSchemas: readRoleSchemas } = useReadSchemas(roleSchema.ETId);

  const [schemasInitialized, setSchemasInitialized] = useState(false);
  const [initializing, setInitializing] = useState(false);

  useEffect(() => {
    const checkAndCreateSchemas = async () => {
      setInitializing(true);

      try {
        await readProfileSchemas();
        if (!profileData) await createSchema(profileSchema.ETId, profileSchema);

        await readBlogSchemas();
        if (!blogData) await createSchema(blogSchema.ETId, blogSchema);

        await readRoleSchemas();
        if (!roleData) await createSchema(roleSchema.ETId, roleSchema);

        setSchemasInitialized(true);
      } catch (error) {
        console.error("Error initializing schemas:", error);
      } finally {
        setInitializing(false);
      }
    };

    checkAndCreateSchemas();
  }, [createSchema, readProfileSchemas, readBlogSchemas, readRoleSchemas, profileData, blogData, roleData]);

  return { schemasInitialized, initializing };
};
