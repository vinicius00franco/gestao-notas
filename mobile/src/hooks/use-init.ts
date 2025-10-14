import { useEffect } from 'react';
import { useGlobalStore } from '../store/global';

export function useInit() {
  const { setDBReady } = useGlobalStore();

  useEffect(() => {
    // In a real app, you would initialize your database here.
    // For this example, we'll just simulate a delay.
    setTimeout(() => {
      setDBReady(true);
    }, 2000);
  }, [setDBReady]);
}