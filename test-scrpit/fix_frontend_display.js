// This is a temporary helper file to debug the data structure
console.log("Frontend display fix for model estimates");

function fixModelDisplay(model_estimates) {
  // Convert nested objects to simple values
  const fixed = {};
  
  for (const [key, value] of Object.entries(model_estimates)) {
    if (typeof value === 'object' && value !== null) {
      // Extract the effort value from the object
      if (value.effort !== undefined) {
        fixed[key] = value.effort;
      } else if (value.estimate !== undefined) {
        fixed[key] = value.estimate;
      } else if (typeof value === 'number') {
        fixed[key] = value;
      } else {
        fixed[key] = 0; // Default value
      }
      
      // Copy metadata with appropriate keys
      if (value.name) {
        fixed[`${key}_name`] = value.name;
      }
      if (value.confidence) {
        fixed[`${key}_confidence`] = value.confidence;
      }
      if (value.type) {
        fixed[`${key}_type`] = value.type;
      }
      if (value.description) {
        fixed[`${key}_description`] = value.description;
      }
    } else {
      fixed[key] = value;
    }
  }
  
  return fixed;
}

// Example usage:
// const fixed = fixModelDisplay(data.estimation.model_estimates);
// console.log(fixed);
