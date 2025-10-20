import { atom } from "recoil";

export const tokenState = atom<string | null>({
  key: "tokenState",
  default: null,
});

export const user = atom({
  key: "user",
  default: null,
});

export const bottomPopupVisibleState = atom<boolean>({
  key: "bottomPopupVisibleState",
  default: false,
});

export const isUserConfiguredState = atom<boolean>({
  key: "isUserConfiguredState",
  default: false,
});

import { ProfileData } from "@/schemas/profileSchema";
export const userState = atom<ProfileData | null>({
  key: "userState",
  default: null,
});

export const userFetched = atom<boolean>({
  key: "userFetched",
  default: false,
});

export const schemasInitializedState = atom<boolean>({
  key: "schemasInitializedState",
  default: false,
});
