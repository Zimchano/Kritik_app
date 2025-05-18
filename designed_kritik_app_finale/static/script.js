document.addEventListener('DOMContentLoaded', function() {
    // Добавление новых полей для сохранений
    const addSaveBtn = document.getElementById('add-save-btn');
    if (addSaveBtn) {
        addSaveBtn.addEventListener('click', function() {
            const container = document.getElementById('saves-container');
            const newSaveItem = document.createElement('div');
            newSaveItem.className = 'save-item';
            newSaveItem.innerHTML = `
                <input type="file" name="save_files" accept=".zip,.rar,.sav">
                <input type="text" name="save_description" placeholder="Описание сохранения">
            `;
            container.appendChild(newSaveItem);
            
            // Анимация добавления
            newSaveItem.style.opacity = '0';
            newSaveItem.style.transform = 'translateY(20px)';
            setTimeout(() => {
                newSaveItem.style.transition = 'all 0.3s ease';
                newSaveItem.style.opacity = '1';
                newSaveItem.style.transform = 'translateY(0)';
            }, 10);
        });
    }
    
    // Анимация заголовка
    const title = document.querySelector('header h1');
    if (title) {
        setInterval(() => {
            title.style.textShadow = `0 0 10px ${getRandomNeonColor()}, 0 0 20px ${getRandomNeonColor()}`;
        }, 2000);
    }
    
    // Функция для случайного неонового цвета
    function getRandomNeonColor() {
        const colors = ['#ff2a6d', '#05d9e8', '#d300c5', '#ff9a03'];
        return colors[Math.floor(Math.random() * colors.length)];
    }
});

// В script.js
document.querySelectorAll('.cyber-input, .cyber-textarea').forEach(input => {
    input.addEventListener('focus', function() {
        this.style.boxShadow = '0 0 15px var(--neon-blue)';
    });
    
    input.addEventListener('blur', function() {
        this.style.boxShadow = '0 0 5px var(--neon-blue)';
    });
});

// Функция для полноэкранного просмотра
function openFullscreen(img) {
    const modal = document.getElementById("fullscreen-modal");
    const modalImg = document.getElementById("fullscreen-image");
    
    modal.style.display = "block";
    modalImg.src = img.src;
    document.body.style.overflow = "hidden";
}

function closeFullscreen() {
    document.getElementById("fullscreen-modal").style.display = "none";
    document.body.style.overflow = "auto";
}

// Функция удаления скриншота
async function deleteScreenshot(screenshotId, btn) {
    if (!confirm('[ПОДТВЕРЖДЕНИЕ]\nУДАЛИТЬ ЭТОТ СКРИНШОТ?')) return;
    
    try {
        const response = await fetch(`/delete_screenshot/${screenshotId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Анимация удаления
            btn.parentElement.style.transform = "scale(0)";
            btn.parentElement.style.opacity = "0";
            setTimeout(() => {
                btn.parentElement.remove();
            }, 300);
        } else {
            alert('ОШИБКА ПРИ УДАЛЕНИИ');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('СЕТЕВАЯ ОШИБКА');
    }
}

// Закрытие по ESC
document.addEventListener('keydown', function(event) {
    if (event.key === "Escape") {
        closeFullscreen();
    }
});

// Удаление сохранения
async function deleteSave(saveId, btn) {
    if (!confirm('[ПОДТВЕРЖДЕНИЕ]\nУДАЛИТЬ ЭТО СОХРАНЕНИЕ?')) return;
    
    try {
        const response = await fetch(`/delete_save/${saveId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Анимация удаления
            btn.closest('li').style.transform = "scale(0)";
            btn.closest('li').style.opacity = "0";
            setTimeout(() => {
                btn.closest('li').remove();
            }, 300);
        } else {
            alert('ОШИБКА ПРИ УДАЛЕНИИ');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('СЕТЕВАЯ ОШИБКА');
    }
}

// Удаление игры
function deleteGame(gameId) {
    if (confirm('Вы уверены, что хотите удалить эту игру? Это действие нельзя отменить.')) {
        fetch(`/delete_game/${gameId}`, {
            method: 'DELETE',
            headers: {
                'Accept': 'application/json',
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Ошибка при удалении игры');
        })
        .then(data => {
            // Редирект на главную страницу
            window.location.href = data.redirect;
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message);
        });
    }
}
