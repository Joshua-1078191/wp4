import React, { useCallback, useEffect, useState } from 'react';

const haalBronnenOp = useCallback(async () => {
  // ... existing fetch logic ...
}, [zoekTerm, typeFilter, categorieFilter]);

useEffect(() => {
  haalBronnenOp();
}, [haalBronnenOp]); 