import { RoleData } from "@/schemas/roleSchema";

export const ensureViewerRole = async (fetchRoles: Function, addRole: Function) => {
  const rolesData = await fetchRoles();

  if (Array.isArray(rolesData)) {
    const viewerRoleExists = rolesData.some((role: RoleData) => role.roleName === "Viewer");

    if (!viewerRoleExists) {
      await addRole({ id: "", roleName: "Viewer", scope: "ReadOnly" });
    }
  } else {
    throw new Error("Roles data is not an array");
  }
};
