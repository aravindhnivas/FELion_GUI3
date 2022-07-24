/** -------------------------- PersistentDB.ts -------------------------- */
import Store from 'electron-store'

export const db = new Store({ name: 'db' })

export type PersistentDB<T> = {
    subscribe: (subscription: (value: T) => void) => () => void;
    set: (value: T) => void;
    update: (update_func: (curr: T) => T) => void;
  };
  
  /** A generic persistent electron-store database according to the Svelte store contract
   * 
   *  @example
   *      import { persistentDB } from "./persistentStore";
   *      export const store = persistentDB<object>("storeKey", {});
   * 
   *      $store = { id: 1 };
   *      console.log($store.id);
   * 
   *  @param {string} storeKey - A unique key in localStorage for the store.
   *                             This will also be the channel name in Broadcast API.
   *  @param {T} initialValue - Initial value of store
   *  @returns {PersistentDB<T>} - A persistent writable store
   */
  export const persistentDB = <T>(storeKey: string, initialValue: T): PersistentDB<T> => {
    let subscriptions: ((value: T) => void)[] = [];
    let storeValue: T;
  
    const safeSetItem = (key: string, value: T) => {
      try {
        db.set(key, value);
      } catch (error) {
        if (error instanceof Error) {
          console.log(error);
        }
      }
    }
  
    const safeGetItem = (key: string) => {
      try {
        return <T>db.get(key);
      } catch (error) {
        if (error instanceof Error) {
          console.log(error);
        }
      }
    }
  
    let currentStoreString = safeGetItem(storeKey);
    
    if (!currentStoreString) {
      storeValue = initialValue;
      safeSetItem(storeKey, storeValue);
    } else {
      storeValue = <T>safeGetItem(storeKey);
    }
  
    let storeChannel: BroadcastChannel | null = new BroadcastChannel(storeKey);
    storeChannel.onmessage = event => {
      storeValue = <T>safeGetItem(storeKey);
      if (event.data === storeKey) {
        subscriptions.forEach(subscriptions => subscriptions(storeValue));
      }
    }
  
    // Subscribes function and returns an unsubscribe function
    const subscribe = (subscription: (value: T) => void) => {
      subscription(storeValue);
      subscriptions = [...subscriptions, subscription];
  
      // If subscribers go from 0 to 1 (after dropping to 0 before) recreate channel
      if (subscription.length === 1 && storeChannel === null) {
        storeChannel = new BroadcastChannel(storeKey);
      }
      const unsubscribe = () => {
        subscriptions = subscriptions.filter(s => s != subscription);
        
        // If subsccribers go from 1 to 0 close channel
        if (storeChannel && subscription.length === 0) {
          storeChannel.close();
          storeChannel = null;
        }
      }
      return unsubscribe;
    }
  
    // Sets stringified value in local storage and calls subscriptions
    const set = (value: T) => {
      storeValue = value;
      safeSetItem(storeKey, value);
      subscriptions.forEach(subscription => subscription(storeValue));
  
      if (storeChannel) {
        storeChannel.postMessage(storeKey);
      }
    }
  
    // Updates store value according to input function
    const update =
      (update_func: (curr: T) => T) => set(update_func(storeValue));
    return { subscribe, set, update };
  }
  