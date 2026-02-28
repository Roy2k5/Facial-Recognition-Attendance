const API_BASE = 'http://localhost:8000/api';

// Tab Navigation
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    // Remove active from all
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active to selected
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

// Register Form
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fullname = document.getElementById('fullname').value;
    const employeeId = document.getElementById('employeeId').value;
    const photoFile = document.getElementById('photo').files[0];
    
    if (!fullname || !employeeId || !photoFile) {
        alert('Vui lòng điền đầy đủ thông tin');
        return;
    }
    
    const formData = new FormData();
    formData.append('fullname', fullname);
    formData.append('employee_id', employeeId);
    formData.append('photo', photoFile);
    
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            alert('✓ Đăng ký thành công!');
            document.getElementById('registerForm').reset();
            document.getElementById('photoPreview').innerHTML = '';
        } else {
            alert('✗ Lỗi: ' + response.statusText);
        }
    } catch (error) {
        alert('✗ Lỗi kết nối: ' + error.message);
    }
});

// Photo Preview
document.getElementById('photo').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            document.getElementById('photoPreview').innerHTML = 
                `<img src="${event.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    }
});

// Camera Feed
let stream = null;
const video = document.getElementById('cameraFeed');

async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'user' } 
        });
        video.srcObject = stream;
    } catch (error) {
        alert('Không thể truy cập camera: ' + error.message);
    }
}

// Start camera when attendance tab is active
document.querySelector('[data-tab="attendance"]').addEventListener('click', startCamera);

// Capture Photo for Attendance
document.getElementById('captureBtn').addEventListener('click', () => {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('image', blob, 'attendance.jpg');
        
        const resultDiv = document.getElementById('attendanceResult');
        resultDiv.textContent = '⏳ Đang xử lý...';
        resultDiv.className = '';
        
        try {
            const response = await fetch(`${API_BASE}/attendance`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                resultDiv.innerHTML = `
                    <div style="text-align: left;">
                        <strong>✓ Điểm danh thành công!</strong><br>
                        Mã NV: ${data.employee_id}<br>
                        Tên: ${data.name}<br>
                        Độ chính xác: ${(data.confidence * 100).toFixed(1)}%
                    </div>
                `;
                resultDiv.className = 'success';
            } else {
                resultDiv.textContent = '✗ ' + (data.message || 'Không nhận diện được khuôn mặt');
                resultDiv.className = 'error';
            }
        } catch (error) {
            resultDiv.textContent = '✗ Lỗi: ' + error.message;
            resultDiv.className = 'error';
        }
    });
});

// Load History
document.getElementById('searchBtn').addEventListener('click', loadHistory);

async function loadHistory() {
    const dateStr = document.getElementById('filterDate').value;
    
    try {
        const url = dateStr 
            ? `${API_BASE}/history?date=${dateStr}`
            : `${API_BASE}/history`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        const tbody = document.getElementById('historyBody');
        
        if (data.records && data.records.length > 0) {
            tbody.innerHTML = data.records.map(record => `
                <tr>
                    <td>${record.employee_id}</td>
                    <td>${record.name}</td>
                    <td>${new Date(record.timestamp).toLocaleString('vi-VN')}</td>
                    <td>${(record.confidence * 100).toFixed(1)}%</td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #999;">Không có dữ liệu</td></tr>';
        }
    } catch (error) {
        alert('Lỗi: ' + error.message);
    }
}

// Clear Data
document.getElementById('clearBtn').addEventListener('click', async () => {
    if (!confirm('Bạn có chắc chắn muốn xóa dữ liệu điểm danh hôm nay?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/attendance/clear`, {
            method: 'POST'
        });
        
        if (response.ok) {
            alert('✓ Đã xóa dữ liệu!');
            loadStats();
        } else {
            alert('✗ Lỗi: ' + response.statusText);
        }
    } catch (error) {
        alert('✗ Lỗi: ' + error.message);
    }
});

// Load Stats
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();
        
        document.getElementById('totalUsers').textContent = data.total_users || 0;
        document.getElementById('attendedUsers').textContent = data.attended_today || 0;
        document.getElementById('absentUsers').textContent = (data.total_users - data.attended_today) || 0;
    } catch (error) {
        console.error('Lỗi tải thống kê:', error);
    }
}

// Load stats on page load
window.addEventListener('load', loadStats);