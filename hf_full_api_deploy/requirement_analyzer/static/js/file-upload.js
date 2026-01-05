// File Upload Handling for Software Effort Estimation Tool

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('requirementsFile');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const fileTypeIcon = document.getElementById('fileTypeIcon');
    const removeFileBtn = document.getElementById('removeFile');
    
    // If any of the required elements don't exist, exit
    if (!dropZone || !fileInput || !fileInfo || !fileName || !fileSize || !fileTypeIcon || !removeFileBtn) return;
    
    // Initialize file upload functionality
    initFileUpload();
    
    function initFileUpload() {
        // Handle file input change
        fileInput.addEventListener('change', handleFileSelection);
        
        // Handle drag and drop
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('file-upload-area-active');
        });
        
        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('file-upload-area-active');
        });
        
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('file-upload-area-active');
            
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                handleFileSelection();
            }
        });
        
        // Handle click on drop zone
        dropZone.addEventListener('click', function() {
            fileInput.click();
        });
        
        // Handle remove file button
        removeFileBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            resetFileInput();
        });
    }
    
    // Handle file selection
    function handleFileSelection() {
        if (fileInput.files && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            
            // Check file size - limit to 10MB
            const maxSize = 10 * 1024 * 1024; // 10MB in bytes
            if (file.size > maxSize) {
                showToast('File size exceeds the limit (10MB). Please upload a smaller file.', 'warning');
                resetFileInput();
                return;
            }
            
            // Check file extension
            const fileExtension = file.name.split('.').pop().toLowerCase();
            const allowedExtensions = ['txt', 'doc', 'docx', 'pdf', 'md'];
            
            if (!allowedExtensions.includes(fileExtension)) {
                showToast(`Unsupported file format: .${fileExtension}\nAllowed formats: ${allowedExtensions.join(', ')}`, 'warning');
                resetFileInput();
                return;
            }
            
            // Update file info display
            updateFileInfo(file);
            
            // Show upload success animation
            dropZone.classList.add('file-upload-success');
            setTimeout(() => {
                dropZone.classList.remove('file-upload-success');
            }, 1500);
        }
    }
    
    // Update file info display
    function updateFileInfo(file) {
        // Update file name
        fileName.textContent = file.name;
        
        // Update file size
        fileSize.textContent = formatFileSize(file.size);
        
        // Update file type icon
        fileTypeIcon.innerHTML = getFileTypeIcon(file.name);
        
        // Show file info section with animation
        fileInfo.classList.remove('show');
        void fileInfo.offsetWidth; // Force reflow for animation
        fileInfo.classList.add('show');
        
        // Add file type class for styling
        const fileExtension = file.name.split('.').pop().toLowerCase();
        fileInfo.className = 'file-info show file-type-' + fileExtension;
        
        // Hide the drop zone message (keep the zone itself for removing file)
        const uploadIcon = dropZone.querySelector('.file-upload-icon');
        const uploadText = dropZone.querySelector('.file-upload-text');
        
        if (uploadIcon && uploadText) {
            uploadIcon.style.display = 'none';
            uploadText.style.display = 'none';
        }
    }
    
    // Reset file input and hide file info
    function resetFileInput() {
        // Clear file input
        fileInput.value = '';
        
        // Reset file info
        fileName.textContent = 'No file selected';
        fileSize.textContent = '0 KB';
        fileTypeIcon.innerHTML = '<i class="bi bi-file-earmark-text fs-1"></i>';
        
        // Hide file info section
        fileInfo.classList.remove('show');
        
        // Show drop zone message again
        const uploadIcon = dropZone.querySelector('.file-upload-icon');
        const uploadText = dropZone.querySelector('.file-upload-text');
        
        if (uploadIcon && uploadText) {
            uploadIcon.style.display = 'block';
            uploadText.style.display = 'block';
        }
    }
    
    // Get appropriate icon for file type
    function getFileTypeIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        
        const iconMap = {
            'pdf': '<i class="bi bi-file-earmark-pdf fs-1 text-danger"></i>',
            'doc': '<i class="bi bi-file-earmark-word fs-1 text-primary"></i>',
            'docx': '<i class="bi bi-file-earmark-word fs-1 text-primary"></i>',
            'txt': '<i class="bi bi-file-earmark-text fs-1 text-secondary"></i>',
            'md': '<i class="bi bi-markdown fs-1 text-success"></i>'
        };
        
        return iconMap[extension] || '<i class="bi bi-file-earmark fs-1"></i>';
    }
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Function to show toast notification (if enhanced.js is not loaded)
    function showToast(message, type) {
        if (window.showToast) {
            // Use the enhanced.js showToast function if available
            window.showToast(message, type);
        } else {
            // Fallback
            alert(message);
        }
    }
});