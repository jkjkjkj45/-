function openModal(doctorName) {
    document.getElementById('doctorName').innerText = doctorName;
  
    // Получаем актуальную дату
    const today = new Date();
    const options = { year: 'numeric', month: 'numeric', day: 'numeric' };
  
    // Генерируем даты на 5 рабочих дней (с понедельника по пятницу)
    const dates = [];
    let i = 0;
    while (dates.length < 5) {
        const nextDate = new Date(today);
        nextDate.setDate(today.getDate() + i);
        const nextDay = nextDate.getDay(); // День недели следующей даты
        if (nextDay !== 0 && nextDay !== 6) { // Пропускаем воскресенье (0) и субботу (6)
            dates.push(nextDate.toLocaleDateString('ru-RU', options));
        }
        i++;
    }
  
    // Заполняем заголовки дат в таблице
    const dateHeaderRow = document.querySelector('#timeTableBody').previousElementSibling.children[1];
    dateHeaderRow.innerHTML = ''; // Очищаем предыдущие заголовки
    dates.forEach(date => {
        const th = document.createElement('th');
        th.innerText = date;
        dateHeaderRow.appendChild(th);
    });
  
    // Генерируем время с 10:00 до 17:30
    const timeSlots = [];
    for (let hour = 10; hour <= 17; hour++) {
        timeSlots.push(`${hour}:00`);
        timeSlots.push(`${hour}:30`);
    }
  
    // Заполняем таблицу
    const timeTableBody = document.getElementById('timeTableBody');
    timeTableBody.innerHTML = '';
  
    // Создаем строки для времени
    timeSlots.forEach(time => {
        const row = document.createElement('tr');
        dates.forEach(date => {
            const cell = document.createElement('td');
            cell.innerText = time;
  
            // Проверяем, занято ли это время
            let isBooked = false;
            
            appointments.forEach(appt => {
                if (appt.doctor_name === doctorName && appt.appointment_time === date + ' ' + time) {
                    isBooked = true;
                    if (appt.user_email === userEmail) {
                        cell.classList.add('booked-by-user');
                    } else {
                        cell.classList.add('booked');
                    }
                }
            });
            if (!isBooked) {
                cell.onclick = () => bookAppointment(doctorName, date, time, cell);
            }
            else {
              cell.onclick = () => bookAppointment(doctorName, date, time, cell);}
            row.appendChild(cell);
        });
        timeTableBody.appendChild(row);
    });
  
    // Показываем модальное окно
    document.getElementById('myModal').style.display = "block";
  }
  
  function bookAppointment(doctorName, date, time, cell) {
    const appointmentData = {
        doctor_name: doctorName,
        appointment_time: date + ' ' + time
    };
  
    fetch('/appointment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(appointmentData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cell.classList.add('booked-by-user');
            cell.onclick = null;
            alert('Вы записались к врачу на ' + time + ' ' + date);
  
        } else {
            alert(data.message);
        }
    })
  }
  
  function closeModal() {
    document.getElementById('myModal').style.display = "none";
  }
  
  // Закрытие модального окна при клике вне его содержимого
  window.onclick = function (event) {
    const modal = document.getElementById('myModal');
    if (event.target == modal) {
        closeModal();
    }
  }