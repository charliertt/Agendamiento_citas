let currentStep = 1;
  let selectedDateTime = {};

  /* Actualiza el título del modal según el paso actual */
  function updateModalTitle(step) {
    const titles = {
      1: 'Paso 1 de 2 - Selecciona el día y hora',
      2: 'Paso 2 de 2 - Ingresa los datos',
      3: 'Confirmación de cita'
    };
    document.getElementById('dynamicModalTitle').textContent = titles[step];
  }

  /* Actualiza los botones del modal según el paso actual */
  function updateButtons(step) {
    const backButton = document.getElementById('backButton');
    const mainButton = document.getElementById('mainActionButton');
    if (step === 1) {
      backButton.style.display = 'none';
      mainButton.textContent = 'Confirmar Horario';
    } else if (step === 2) {
      backButton.style.display = 'inline-block';
      mainButton.textContent = 'Confirmar Datos';
    } else {
      backButton.style.display = 'none';
      mainButton.textContent = 'Cerrar';
    }
  }

  /* Función para avanzar en los pasos del modal */
  function nextStep() {
    if (currentStep === 1) {
      if (!selectedDateTime.fullDate) {
        alert('Por favor selecciona un horario');
        return;
      }
      document.getElementById('step1').style.display = 'none';
      document.getElementById('step2').style.display = 'block';
      // Actualización de datos de confirmación (se pueden reemplazar los valores fijos por los seleccionados)
      document.getElementById('confirmation-psychologist').textContent = 'Carlos';
      document.getElementById('confirmation-specialty').textContent = 'Pediatría';
      document.getElementById('confirmation-date').textContent = 'Lunes 24 de febrero';
      document.getElementById('confirmation-time').textContent = '09:00';
      currentStep = 2;
    } else if (currentStep === 2) {
      if (document.getElementById('appointmentForm').checkValidity()) {
        document.getElementById('step2').style.display = 'none';
        document.getElementById('confirmation').style.display = 'block';
        // Actualización final de datos
        document.getElementById('final-psychologist').textContent = 'Carlos - Pediatría';
        document.getElementById('final-datetime').textContent = 'Lunes 24 de febrero a las 09:00';
        document.getElementById('final-email').textContent = 'nombre@mail.com';
        currentStep = 3;
      } else {
        alert('Por favor completa todos los campos requeridos');
        return;
      }
    } else {
      // Cerrar el modal
      bootstrap.Modal.getInstance(document.getElementById('horasModal')).hide();
      return;
    }
    updateModalTitle(currentStep);
    updateButtons(currentStep);
  }

  /* Función para volver al paso anterior */
  function previousStep() {
    if (currentStep === 2) {
      document.getElementById('step2').style.display = 'none';
      document.getElementById('step1').style.display = 'block';
      currentStep = 1;
    }
    updateModalTitle(currentStep);
    updateButtons(currentStep);
  }

  /* Evento para la selección de un horario */
  document.addEventListener('click', function(event) {
    if (event.target.classList.contains('time-btn')) {
      // Remover selección previa
      document.querySelectorAll('.time-btn').forEach(btn => btn.classList.remove('selected'));
      event.target.classList.add('selected');

      const selectedDayBtn = document.querySelector('.day-btn.active');
                if (!selectedDayBtn) return;

                // Extrae año, mes y día del dataset (recordando que el mes en Date es 0-indexado)
                const parts = selectedDayBtn.dataset.date.split('-'); // ["2025", "02", "18"]
                const date = new Date(parts[0], parts[1] - 1, parts[2]);

                const options = { weekday: 'long', day: 'numeric', month: 'long' };
                const formattedDate = date.toLocaleDateString('es-ES', options);
                const formattedTime = event.target.textContent.trim();

                document.getElementById('selectedDateTimeText').textContent = `${formattedDate} a las ${formattedTime}`;
                document.getElementById('selectedTimeDisplay').style.display = 'block';

                selectedDateTime = {
                fullDate: `${formattedDate} a las ${formattedTime}`,
                dateObject: date,
                time: formattedTime
                };

    }
  });

  /* Reinicia el modal al abrirlo */
  document.getElementById('horasModal').addEventListener('show.bs.modal', function(event) {
    currentStep = 1;
    selectedDateTime = {};
    updateModalTitle(1);
    updateButtons(1);
    document.getElementById('step1').style.display = 'block';
    document.getElementById('step2').style.display = 'none';
    document.getElementById('confirmation').style.display = 'none';
    
    // Limpia el contenido del mensaje de "Cita seleccionada"
    document.getElementById('selectedDateTimeText').textContent = '';
    document.getElementById('selectedTimeDisplay').style.display = 'none';
    
    // Elimina clases de selección previa en los botones
    document.querySelectorAll('.day-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.time-btn').forEach(btn => btn.classList.remove('selected'));
  });
  

  /* Inicialización del carrusel y días disponibles */
  document.addEventListener('DOMContentLoaded', () => {
    const daysShort = ['DOM', 'LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB'];
    const monthsShort = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];
    const fullDays = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    const today = new Date();

    // Calcular el lunes de la semana actual
    const dayOfWeek = today.getDay();
    const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    const currentMonday = new Date(today);
    currentMonday.setDate(today.getDate() + mondayOffset);

    /* Función que genera un array con 7 días a partir de una fecha */
    function getWeekDates(startDate) {
      const days = [];
      for (let i = 0; i < 7; i++) {
        const d = new Date(startDate);
        d.setDate(d.getDate() + i);
        days.push(d);
      }
      return days;
    }

    const currentWeek = getWeekDates(currentMonday);
    const nextMonday = new Date(currentMonday);
    nextMonday.setDate(nextMonday.getDate() + 7);
    const nextWeek = getWeekDates(nextMonday);

    /* Inyecta en el DOM los días y fechas en el carrusel */
    function renderWeek(weekArray, weekdaysContainerId, weekdatesContainerId) {
      const weekdaysContainer = document.getElementById(weekdaysContainerId);
      const weekdatesContainer = document.getElementById(weekdatesContainerId);
      if (!weekdaysContainer || !weekdatesContainer) return;

      weekdaysContainer.innerHTML = '';
      weekdatesContainer.innerHTML = '';

      weekArray.forEach(dateObj => {
        const dayShort = daysShort[dateObj.getDay()];
        const fullDay = fullDays[dateObj.getDay()];
        const dayNum = dateObj.getDate();
        const monthName = monthsShort[dateObj.getMonth()];

        // Día de la semana (texto)
        const daySpan = document.createElement('span');
        daySpan.classList.add('text-center');
        daySpan.textContent = dayShort;
        weekdaysContainer.appendChild(daySpan);

        // Botón para la fecha
        const dayBtn = document.createElement('button');
        dayBtn.classList.add('day-btn', 'btn', 'btn-primary');
        dayBtn.innerHTML = `${dayNum}<br>${monthName}`;
        dayBtn.dataset.day = fullDay;
        dayBtn.dataset.date = dateObj.toISOString().split('T')[0];

        dayBtn.addEventListener('click', function () {
          document.querySelectorAll('.day-btn').forEach(b => b.classList.remove('active', 'btn-primary'));
          this.classList.add('active', 'btn-primary');
          filterHorarios(this.dataset.day);
        });

        weekdatesContainer.appendChild(dayBtn);
      });
    }

    renderWeek(currentWeek, 'weekdays-current', 'weekdates-current');
    renderWeek(nextWeek, 'weekdays-next', 'weekdates-next');

    /* Filtra y muestra únicamente los horarios del día seleccionado */
    function filterHorarios(selectedDay) {
      const activePsicologo = document.querySelector('#horarioSection .psicologo:not([style*="display: none"])');
      if (!activePsicologo) return;
      activePsicologo.querySelectorAll('.horario-container').forEach(container => {
        container.style.display = container.dataset.day === selectedDay ? 'block' : 'none';
      });
    }

    /* Al abrir el modal, se actualizan los días disponibles para el psicólogo seleccionado */
    const horasModal = document.getElementById('horasModal');
    horasModal.addEventListener('show.bs.modal', function(event) {
      const button = event.relatedTarget;
      const psicologo = button.getAttribute('data-psicologo');

      // Ocultar todos los horarios de psicólogos
      document.querySelectorAll('#horarioSection .psicologo').forEach(el => {
        el.style.display = 'none';
      });

      const target = document.querySelector(`#horarioSection .psicologo[data-psicologo="${psicologo}"]`);
      if (target) {
        target.style.display = 'block';
        const availableDays = target.dataset.diasDisponibles.split(',');
        const today = new Date();
        document.querySelectorAll('.day-btn').forEach(btn => {
          const buttonDate = new Date(btn.dataset.date);
          const isAvailable = availableDays.includes(btn.dataset.day);
          const isNotPast = buttonDate >= today.setHours(0,0,0,0);
          btn.disabled = !(isAvailable && isNotPast);
          btn.classList.toggle('btn-primary', isAvailable && isNotPast);
          btn.classList.toggle('btn-secondary', !(isAvailable && isNotPast));
        });
        const todayName = fullDays[today.getDay()];
        filterHorarios(todayName);
      }
    });
  });