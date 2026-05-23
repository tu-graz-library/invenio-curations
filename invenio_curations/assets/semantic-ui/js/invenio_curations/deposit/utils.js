/*
 * SPDX-FileCopyrightText: 2024 Graz University of Technology.
 * SPDX-FileCopyrightText: 2024 TU Wien.
 * SPDX-License-Identifier: MIT
 */

// Copied from rdm-records to not depend on it.
export const getInputFromDOM = (elementName) => {
  const element = document.getElementsByName(elementName);
  if (element.length > 0 && element[0].hasAttribute("value")) {
    return JSON.parse(element[0].value);
  }
  return null;
};
