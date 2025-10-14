import { create } from 'zustand';

interface GlobalState {
  isDBReady: boolean;
  setDBReady: (isReady: boolean) => void;
}

export const useGlobalStore = create<GlobalState>((set) => ({
  isDBReady: false,
  setDBReady: (isReady) => set({ isDBReady: isReady }),
}));