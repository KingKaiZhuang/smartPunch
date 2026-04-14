/* ==================== 
   搜尋和匯出頁面 - JavaScript (多格式版)
   ==================== */

/**
 * 初始化搜尋和匯出功能
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeExportButton();
    initializeAutoScroll();
});

/**
 * 初始化匯出按鈕
 */
function initializeExportButton() {
    var exportBtn = document.getElementById('exportBtn');
    var nidValue = document.querySelector('input[name="nid"]').value;
    var dateStart = document.querySelector('input[name="date_start"]').value;
    var dateEnd = document.querySelector('input[name="date_end"]').value;
    
    var hasSearch = nidValue || dateStart || dateEnd;
    var hasResults = document.querySelector('table') !== null;

    if (hasSearch && hasResults) {
        exportBtn.style.display = 'inline-block';
        exportBtn.addEventListener('click', handleExportClick);
    }
}

/**
 * 處理匯出按鈕點擊事件
 */
function handleExportClick(e) {
    e.preventDefault();
    
    var nidValue = document.querySelector('input[name="nid"]').value;
    var dateStart = document.querySelector('input[name="date_start"]').value;
    var dateEnd = document.querySelector('input[name="date_end"]').value;

    // 顯示格式選擇對話框
    showFormatModal(nidValue, dateStart, dateEnd);
}

/**
 * 顯示格式選擇對話框
 */
function showFormatModal(nid, dateStart, dateEnd) {
    var modalHTML = `
        <div id="formatModal" class="modal-overlay">
            <div class="modal-content">
                <h3>選擇匯出格式</h3>
                <div class="format-options">
                    <div class="format-option">
                        <input type="radio" id="format-detailed" name="export-format" value="detailed" checked>
                        <label for="format-detailed">
                            <strong>📋 詳細格式</strong><br>
                            <span class="format-desc">每筆記錄單獨一行，顯示所有詳細資訊</span>
                        </label>
                    </div>
                    <div class="format-option">
                        <input type="radio" id="format-summary" name="export-format" value="summary">
                        <label for="format-summary">
                            <strong>📊 統計格式</strong><br>
                            <span class="format-desc">按人員統計，每人一行，自動合併計算</span>
                        </label>
                    </div>
                </div>
                <div class="modal-actions">
                    <button class="btn-cancel" onclick="closeFormatModal()">取消</button>
                    <button class="btn-export" onclick="submitExport('${nid}', '${dateStart}', '${dateEnd}')">確認匯出</button>
                </div>
            </div>
        </div>
    `;

    // 移除已存在的 modal
    var existingModal = document.getElementById('formatModal');
    if (existingModal) {
        existingModal.remove();
    }

    // 添加 modal 到頁面
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // 添加 CSS（如果還沒有）
    if (!document.getElementById('modalStyles')) {
        addModalStyles();
    }
}

/**
 * 關閉 Modal
 */
function closeFormatModal() {
    var modal = document.getElementById('formatModal');
    if (modal) {
        modal.remove();
    }
}

/**
 * 提交匯出
 */
function submitExport(nid, dateStart, dateEnd) {
    var format = document.querySelector('input[name="export-format"]:checked').value;
    
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = '/export_xlsx';
    form.style.display = 'none';

    var nidInput = document.createElement('input');
    nidInput.type = 'hidden';
    nidInput.name = 'nid';
    nidInput.value = nid;
    form.appendChild(nidInput);

    var dateStartInput = document.createElement('input');
    dateStartInput.type = 'hidden';
    dateStartInput.name = 'date_start';
    dateStartInput.value = dateStart;
    form.appendChild(dateStartInput);

    var dateEndInput = document.createElement('input');
    dateEndInput.type = 'hidden';
    dateEndInput.name = 'date_end';
    dateEndInput.value = dateEnd;
    form.appendChild(dateEndInput);

    var formatInput = document.createElement('input');
    formatInput.type = 'hidden';
    formatInput.name = 'format';
    formatInput.value = format;
    form.appendChild(formatInput);

    document.body.appendChild(form);
    form.submit();
    
    setTimeout(function() {
        document.body.removeChild(form);
        closeFormatModal();
    }, 1000);
}

/**
 * 添加 Modal 樣式
 */
function addModalStyles() {
    var style = document.createElement('style');
    style.id = 'modalStyles';
    style.textContent = `
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            max-width: 450px;
            width: 90%;
            animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
            from {
                transform: translateY(20px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .modal-content h3 {
            margin: 0 0 20px 0;
            color: #333;
            font-size: 20px;
        }

        .format-options {
            margin-bottom: 25px;
        }

        .format-option {
            display: flex;
            align-items: flex-start;
            margin-bottom: 15px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .format-option:hover {
            border-color: #1a73e8;
            background: #f8f9fa;
        }

        .format-option input[type="radio"] {
            margin-top: 3px;
            margin-right: 12px;
            cursor: pointer;
            width: 18px;
            height: 18px;
            flex-shrink: 0;
        }

        .format-option label {
            cursor: pointer;
            flex: 1;
            margin: 0;
        }

        .format-option strong {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-size: 15px;
        }

        .format-desc {
            display: block;
            color: #999;
            font-size: 13px;
        }

        .modal-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }

        .btn-cancel, .btn-export {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        .btn-cancel {
            background: #f0f0f0;
            color: #333;
        }

        .btn-cancel:hover {
            background: #e0e0e0;
        }

        .btn-export {
            background: #1a73e8;
            color: white;
        }

        .btn-export:hover {
            background: #1557b0;
            box-shadow: 0 4px 12px rgba(26, 115, 232, 0.3);
            transform: translateY(-2px);
        }

        @media (max-width: 480px) {
            .modal-content {
                padding: 20px;
            }

            .modal-content h3 {
                font-size: 18px;
                margin-bottom: 15px;
            }

            .format-option {
                padding: 12px;
                margin-bottom: 12px;
            }

            .format-option input[type="radio"] {
                width: 16px;
                height: 16px;
            }

            .modal-actions {
                flex-direction: column;
            }

            .btn-cancel, .btn-export {
                width: 100%;
            }
        }
    `;
    document.head.appendChild(style);
}

/**
 * 初始化自動滾動功能
 */
function initializeAutoScroll() {
    var nidValue = document.querySelector('input[name="nid"]').value;
    var dateStart = document.querySelector('input[name="date_start"]').value;
    var dateEnd = document.querySelector('input[name="date_end"]').value;
    
    var hasSearch = nidValue || dateStart || dateEnd;

    if (hasSearch) {
        setTimeout(function() {
            var resultSection = document.querySelector('.results-section');
            if (resultSection) {
                resultSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }, 100);
    }
}