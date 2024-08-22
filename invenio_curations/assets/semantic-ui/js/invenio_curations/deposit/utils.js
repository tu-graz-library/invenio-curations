// This file is part of InvenioRDM
// Copyright (C) 2024 Graz University of Technology.
// Copyright (C) 2024 TU Wien.
//
// Invenio-curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

// Copied from rdm-records to not depend on it.
export const getInputFromDOM = (elementName) => {
  const element = document.getElementsByName(elementName);
  if (element.length > 0 && element[0].hasAttribute("value")) {
    return JSON.parse(element[0].value);
  }
  return null;
};
