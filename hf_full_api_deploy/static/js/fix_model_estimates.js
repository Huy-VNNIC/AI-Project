// Create a fix for the main.js file
// This function can be inserted at the top of showResults() to fix the model_estimates

function fixModelEstimates(modelEstimates) {
  if (!modelEstimates || typeof modelEstimates !== 'object') {
    return {};
  }
  
  const fixed = {};
  
  Object.entries(modelEstimates).forEach(([key, value]) => {
    // Skip metadata fields
    if (key.endsWith('_name') || key.endsWith('_confidence') || 
        key.endsWith('_type') || key.endsWith('_description')) {
      return;
    }
    
    let modelData = {
      name: key,
      effort: 0,
      confidence: 70,
      type: '',
      description: ''
    };
    
    // Handle the case where value is an object
    if (value && typeof value === 'object') {
      // Extract values from the object
      if (value.name) modelData.name = value.name;
      
      // Get effort value
      if (value.effort !== undefined) {
        modelData.effort = value.effort;
      } else if (value.estimate !== undefined) {
        modelData.effort = value.estimate;
      } else if (value.effort_pm !== undefined) {
        modelData.effort = value.effort_pm;
      }
      
      // Get confidence value
      if (value.confidence !== undefined) {
        modelData.confidence = value.confidence;
      }
      
      // Get type value
      if (value.type !== undefined) {
        modelData.type = value.type;
      } else {
        // Derive type from key
        if (key.toLowerCase().includes('cocomo')) {
          modelData.type = 'COCOMO';
        } else if (key.toLowerCase().includes('function_points')) {
          modelData.type = 'Function Points';
        } else if (key.toLowerCase().includes('use_case')) {
          modelData.type = 'Use Case';
        } else if (key.toLowerCase().includes('loc')) {
          modelData.type = 'LOC';
        } else if (key.toLowerCase().includes('ml_')) {
          modelData.type = 'ML';
        } else {
          modelData.type = 'Other';
        }
      }
      
      // Get description value
      if (value.description !== undefined) {
        modelData.description = value.description;
      }
    }
    // Handle the case where value is a number
    else if (typeof value === 'number') {
      modelData.effort = value;
      
      // Derive type from key
      if (key.toLowerCase().includes('cocomo')) {
        modelData.type = 'COCOMO';
      } else if (key.toLowerCase().includes('function_points')) {
        modelData.type = 'Function Points';
      } else if (key.toLowerCase().includes('use_case')) {
        modelData.type = 'Use Case';
      } else if (key.toLowerCase().includes('loc')) {
        modelData.type = 'LOC';
      } else if (key.toLowerCase().includes('ml_')) {
        modelData.type = 'ML';
      } else {
        modelData.type = 'Other';
      }
    }
    
    // Add the fixed model to the result
    fixed[key] = modelData;
  });
  
  return fixed;
}

// To use this function:
// Inside showResults():
// if (data.estimation?.model_estimates) {
//   data.estimation.model_estimates = fixModelEstimates(data.estimation.model_estimates);
// }
