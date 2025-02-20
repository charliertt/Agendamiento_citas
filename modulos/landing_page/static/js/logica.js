document.addEventListener('DOMContentLoaded', () => {
  // Variables globales del modal
  let currentStep = 1;
  let selectedDateTime = {};
  let selectedPsychologist = '';
  let selectedSpecialty = '';

  /* Actualiza el título del modal según el paso actual */
  function updateModalTitle(step) {
    const titles = {
      1: 'Paso 1 de 2 ',
      2: 'Paso 2 de 2 - Ingresa los datos',
      3: 'Confirmación de Cita'
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
      document.getElementById('selectDayTitle').style.display = 'none';
      document.getElementById('titulo').style.display = 'none';
      
  
      // Actualiza los datos de confirmación en step2
      document.getElementById('confirmation-psychologist').textContent = selectedPsychologist;
      document.getElementById('confirmation-specialty').textContent = selectedSpecialty;
      const formattedConfirmationDate = selectedDateTime.dateObject.toLocaleDateString('es-ES', {
        weekday: 'long',
        day: 'numeric',
        month: 'long'
      });
      document.getElementById('confirmation-date').textContent = formattedConfirmationDate;
      document.getElementById('confirmation-time').textContent = selectedDateTime.time;
  
      currentStep = 2;
    } else if (currentStep === 2) {
      const form = document.getElementById('appointmentForm');
      if (form.checkValidity()) {
        // Prepara los datos y actualiza los hidden
        if (selectedDateTime.dateObject) {
          // Formateamos la fecha en formato local YYYY-MM-DD
          const day = selectedDateTime.dateObject.getDate().toString().padStart(2, '0');
          const month = (selectedDateTime.dateObject.getMonth() + 1).toString().padStart(2, '0');
          const year = selectedDateTime.dateObject.getFullYear();
          document.getElementById('hiddenDateField').value = `${year}-${month}-${day}`;
          document.getElementById('hiddenTimeField').value = selectedDateTime.time;
        }
        
        document.getElementById('hiddenPsicologoField').value = selectedPsychologist;
        document.getElementById('hiddenPsicologoFieldID').value = selectedPsycholoid;
  
        // Envía el formulario vía AJAX
        const formData = new FormData(form);
        fetch(form.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Actualiza la sección final del modal con los datos de confirmación
            document.getElementById('final-psychologist').textContent = data.psychologist;
            document.getElementById('final-datetime').textContent = data.datetime;
            document.getElementById('final-email').textContent = data.email;
  
            // Oculta el step2 y muestra la confirmación final
            document.getElementById('step2').style.display = 'none';
            document.getElementById('confirmation').style.display = 'block';
            currentStep = 3;
            updateModalTitle(currentStep);
            updateButtons(currentStep);
          } else {
            console.error('Error al agendar la cita:', data.error);
            console.log('Detalles del error:', data.errors);
            alert('Error al agendar la cita: ' + data.error);
          }
        })
        .catch(error => {
          console.error(error);
          alert('Error en el servidor.');
        });
      } else {
        alert('Por favor completa todos los campos requeridos');
        return;
      }
    } else {
      // Cierra el modal
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
  
  // Expone las funciones para que sean accesibles desde los atributos onclick en el HTML
  window.nextStep = nextStep;
  window.previousStep = previousStep;
  
  /* Evento para la selección de un horario */
  document.addEventListener('click', function (event) {
    if (event.target.classList.contains('time-btn')) {
      // Remueve selección previa y agrega la actual
      document.querySelectorAll('.time-btn').forEach(btn => btn.classList.remove('selected'));
      event.target.classList.add('selected');
  
      const selectedDayBtn = document.querySelector('.day-btn.active');
      if (!selectedDayBtn) return;
  
      // Obtiene la fecha local a partir del dataset (formato YYYY-MM-DD)
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
  
      // Actualiza los campos hidden utilizando el formato local YYYY-MM-DD
      if (selectedDateTime.dateObject) {
        const day = selectedDateTime.dateObject.getDate().toString().padStart(2, '0');
        const month = (selectedDateTime.dateObject.getMonth() + 1).toString().padStart(2, '0');
        const year = selectedDateTime.dateObject.getFullYear();
        document.getElementById('hiddenDateField').value = `${year}-${month}-${day}`;
        document.getElementById('hiddenTimeField').value = selectedDateTime.time;
      }
    }
    
    // Actualiza el campo hidden del psicólogo usando selectedPsychologist (asegúrate que tenga el ID correcto)
    if (selectedPsychologist) {
      document.getElementById('hiddenPsicologoField').value = selectedPsychologist;
    }
  });
  
  /* ------------------ Configuración del carrusel de días ------------------ */
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
  
      // Elemento para mostrar el día (texto)
      const daySpan = document.createElement('span');
      daySpan.classList.add('text-center');
      daySpan.textContent = dayShort;
      weekdaysContainer.appendChild(daySpan);
  
      // Botón para la fecha
      const dayBtn = document.createElement('button');
      dayBtn.classList.add('day-btn', 'btn', 'btn-primary');
      dayBtn.innerHTML = `${dayNum}<br>${monthName}`;
      dayBtn.dataset.day = fullDay;
      
      // Usamos formato local (YYYY-MM-DD) en lugar de toISOString para evitar desfases
      const day = dateObj.getDate().toString().padStart(2, '0');
      const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
      const year = dateObj.getFullYear();
      dayBtn.dataset.date = `${year}-${month}-${day}`;
  
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
  
  /* ------------------ Evento al abrir el modal ------------------ */
  document.getElementById('horasModal').addEventListener('show.bs.modal', function (event) {
    // Reinicia el estado del modal
    currentStep = 1;
    selectedDateTime = {};
    updateModalTitle(1);
    updateButtons(1);
    document.getElementById('step1').style.display = 'block';
    document.getElementById('step2').style.display = 'none';
    document.getElementById('confirmation').style.display = 'none';
    document.getElementById('selectedDateTimeText').textContent = '';
    document.getElementById('selectedTimeDisplay').style.display = 'none';
    document.querySelectorAll('.day-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.time-btn').forEach(btn => btn.classList.remove('selected'));
  
    // Captura la información del botón que abrió el modal
    const button = event.relatedTarget;
    selectedPsychologist = button.getAttribute('data-psicologo');
    selectedPsycholoid = button.getAttribute('data-psicologo-id');
    console.log(selectedPsycholoid);
    selectedSpecialty = button.getAttribute('data-especialidad') || '';
  
    // Actualiza la sección de horarios para el psicólogo seleccionado
    document.querySelectorAll('#horarioSection .psicologo').forEach(el => {
      el.style.display = 'none';
    });
  
    const target = document.querySelector(`#horarioSection .psicologo[data-psicologo="${selectedPsychologist}"]`);
    if (target) {
      target.style.display = 'block';
      const availableDays = target.dataset.diasDisponibles.split(',');
      const today = new Date();
      document.querySelectorAll('.day-btn').forEach(btn => {
        const buttonDate = new Date(btn.dataset.date);
        const isAvailable = availableDays.includes(btn.dataset.day);
        const todayStart = new Date();
        todayStart.setHours(0, 0, 0, 0);
        const isNotPast = buttonDate >= todayStart;
        btn.disabled = !(isAvailable && isNotPast);
        btn.classList.toggle('btn-primary', isAvailable && isNotPast);
        btn.classList.toggle('btn-secondary', !(isAvailable && isNotPast));
      });
      const todayName = fullDays[today.getDay()];
      filterHorarios(todayName);
    }
  });
});
