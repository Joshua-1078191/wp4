import React, { useEffect, useCallback } from 'react';

const fetchData = useCallback(() => {
  // ... existing fetch logic ...
}, []);

useEffect(() => {
  fetchData();
}, [fetchData]); 