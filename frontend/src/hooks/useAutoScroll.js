/**
 * Custom hook for auto-scrolling to bottom of messages
 */

import { useEffect, useRef } from 'react';
import { scrollToElement } from '../utils/helpers';
import { UI_CONFIG } from '../utils/constants';

/**
 * Hook to automatically scroll to the bottom of a container
 * @param {Array} dependencies - Dependencies that trigger scroll (e.g., messages array)
 * @param {boolean} enabled - Whether auto-scroll is enabled
 * @returns {Object} Ref to attach to scroll target element
 */
export const useAutoScroll = (dependencies = [], enabled = true) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (enabled && scrollRef.current) {
      scrollToElement(scrollRef.current, {
        behavior: UI_CONFIG.AUTO_SCROLL_BEHAVIOR,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...dependencies, enabled]);

  return scrollRef;
};

export default useAutoScroll;
