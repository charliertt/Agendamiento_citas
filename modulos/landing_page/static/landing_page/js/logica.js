document.addEventListener('DOMContentLoaded', () => {
  // Variables globales del modal
  let currentStep = 1;
  let selectedDateTime = {};
  let selectedPsychologist = '';
  let selectedSpecialty = '';
  let selectedPsycholoid = '';
  let verifiedEmail = '';  // Guardará el email ingresado

  /* Actualiza el título del modal según el paso actual */
  function updateModalTitle(step) {
    const step2AVisible = window.getComputedStyle(document.getElementById('step2A')).display !== 'none';
    if (step2AVisible) {
      document.getElementById('dynamicModalTitle').textContent = 'Confirmar Identidad';
    } else {
      const titles = {
        1: 'Selecciona Día - Hora',
        2: '🎯 Confirmación de Cita',
        3: 'Confirmación'
      };
      document.getElementById('dynamicModalTitle').textContent = titles[step] || '';
    }
  }
  

  function updateButtons(step) {
    const step2AElement = document.getElementById('step2A');
    const step2AVisible = step2AElement && window.getComputedStyle(step2AElement).display !== 'none';
    
    const backButton = document.getElementById('backButton');
    const mainButton = document.getElementById('mainActionButton');
  
    // Ocultar siempre el botón principal si step2A está visible
    if (step2AVisible) {
      mainButton.style.display = 'none';
      backButton.style.display = 'inline-block';
      backButton.style.float = 'left';
      return;
    }
  
    // Resto de la lógica original para otros pasos
    if (step === 1) {
      backButton.style.display = 'none';
      mainButton.textContent = 'Confirmar Horario';
      mainButton.style.display = 'inline-block';
      mainButton.style.margin = '0 auto';
    } else if (step === 2) {
      backButton.style.display = 'inline-block';
      mainButton.textContent = 'Confirmar Datos';
      mainButton.style.display = 'inline-block';
      mainButton.style.margin = '0 auto';
    } else {
      backButton.style.display = 'none';
      mainButton.textContent = 'Cerrar';
      mainButton.style.display = 'inline-block';
    }
  }
  

  /* Función para precargar campos en el formulario */
  function precargarCampos(userData) {
    if (userData.first_name) {
      document.getElementById('id_first_name').value = userData.first_name;
    }
    if (userData.last_name) {
      document.getElementById('id_last_name').value = userData.last_name;
    }
    if (userData.username) {
      document.getElementById('id_username').value = userData.username;
    }
    if (userData.tipo_identificacion) {
      document.getElementById('id_tipo_identificacion').value = userData.tipo_identificacion;
    }
    if (userData.identificacion) {
      document.getElementById('id_identificacion').value = userData.identificacion;
    }
    if (userData.eps) {
      document.getElementById('id_eps').value = userData.eps;
    }
    if (userData.alergias) {
      document.getElementById('id_alergias').value = userData.alergias;
    }
    if (userData.enfermedades) {
      document.getElementById('id_enfermedades').value = userData.enfermedades;
    }
    // El email se asigna en otra parte, pero podrías también precargarlo aquí:
    if (userData.email) {
      document.getElementById('appointmentForm').elements['email'].value = userData.email;
    }
  }
  

  /* Función que muestra el formulario de datos (paso 2) tras la verificación del email */
  function mostrarFormulario(isNew, userData) {
    // Oculta el bloque de verificación de email (step2A)
    document.getElementById('step2A').style.display = 'none';
    // Muestra el bloque del formulario de datos (step2)
    document.getElementById('step2').style.display = 'block';
    currentStep = 2;
    updateModalTitle(currentStep);
    updateButtons(currentStep);
    
    // Asigna el email al formulario
    document.getElementById('appointmentForm').elements['email'].value = verifiedEmail;
    
    if (!isNew && userData) {
      // Usuario existente: precarga los campos y oculta el contenedor de contraseñas
      precargarCampos(userData);
      document.getElementById('passwordFields').style.display = 'none';
      document.querySelectorAll('#passwordFields input').forEach(input => {
        input.disabled = true;
      });
    } else {
      // Usuario nuevo: muestra los campos de contraseña
      document.getElementById('passwordFields').style.display = 'block';
      document.querySelectorAll('#passwordFields input').forEach(input => {
        input.disabled = false;
      });
    }
  }
  

  /* Asigna el listener para el botón de verificación del correo una sola vez */
  document.getElementById('verifyEmailBtn').addEventListener('click', function() {
    const email = document.getElementById('emailInput').value.trim();
    if (!email) {
      alert('Ingresa un correo válido.');
      return;
    }
    verifiedEmail = email;
    fetch('/verificar_usuario/', {  // Ajusta la URL a tu endpoint
      method: 'POST',
      headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email: email })
    })
    .then(res => res.json())
    .then(data => {
      if (data.exists) {
        // Si el usuario existe, precarga los datos en el formulario
        mostrarFormulario(false, data.user_data);
      } else {
        // Si el usuario no existe, muestra el formulario para que ingrese sus datos
        mostrarFormulario(true);
      }
    })
    .catch(err => console.error(err));
  });

  /* Función para avanzar en los pasos del modal */
  function nextStep() {
    if (currentStep === 1) {
      if (!selectedDateTime.fullDate) {
        alert('Por favor selecciona un horario');
        return;
      }
      // Oculta el paso 1 y muestra el bloque de verificación (step2A)
      document.getElementById('step1').style.display = 'none';
      document.getElementById('step2A').style.display = 'block';
      document.getElementById('selectDayTitle').style.display = 'none';
      document.getElementById('titulo').style.display = 'none';

      // Actualiza datos de confirmación para el paso 2
      document.getElementById('confirmation-psychologist').textContent = selectedPsychologist;
      document.getElementById('confirmation-specialty').textContent = selectedSpecialty;
      const formattedConfirmationDate = selectedDateTime.dateObject.toLocaleDateString('es-ES', {
        weekday: 'long',
        day: 'numeric',
        month: 'long'
      });
      document.getElementById('confirmation-date').textContent = formattedConfirmationDate;
      document.getElementById('confirmation-time').textContent = selectedDateTime.time;
      // Se espera la verificación del email aquí.
    } else if (currentStep === 2) {
      const form = document.getElementById('appointmentForm');
      if (form.checkValidity()) {
        // Actualiza los campos hidden con la fecha y hora seleccionadas
        if (selectedDateTime.dateObject) {
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

            // Oculta el paso 2 y muestra la confirmación final
            document.getElementById('step2').style.display = 'none';
            document.getElementById('confirmation').style.display = 'block';
            currentStep = 3;
            updateModalTitle(currentStep);
            updateButtons(currentStep);

            form.reset();
            document.getElementById('emailInput').value = ''; // Limpiar email de verificación
            verifiedEmail = '';
            selectedDateTime = {};
            selectedPsychologist = '';
            selectedSpecialty = '';
            selectedPsycholoid = '';
            
            // Limpiar campos ocultos
            document.getElementById('hiddenDateField').value = '';
            document.getElementById('hiddenTimeField').value = '';
            document.getElementById('hiddenPsicologoField').value = '';
            document.getElementById('hiddenPsicologoFieldID').value = '';

            // Restablecer campos de contraseña
            document.getElementById('passwordFields').style.display = 'block';
            document.querySelectorAll('#passwordFields input').forEach(input => {
              input.disabled = false;
              input.value = '';
            });

            // Limpiar selección de horario
            document.querySelectorAll('.time-btn').forEach(btn => btn.classList.remove('selected'));
            document.getElementById('selectedTimeDisplay').style.display = 'none';
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
    } else if (currentStep === 3) {
      // Cierra el modal
      bootstrap.Modal.getInstance(document.getElementById('horasModal')).hide();
      return;
    }
    updateModalTitle(currentStep);
    updateButtons(currentStep);
  }

  /* Función para volver al paso anterior */
  function previousStep() {
    const step2AElement = document.getElementById('step2A');
    const isStep2AVisible = step2AElement && window.getComputedStyle(step2AElement).display !== 'none';
  
    if (isStep2AVisible) {
      // Si estamos en step2A, volver a step1
      document.getElementById('step2A').style.display = 'none';
      document.getElementById('step1').style.display = 'block';
      currentStep = 1;
    } else if (currentStep === 2) {
      // Si estamos en step2, volver a step2A
      document.getElementById('step2').style.display = 'none';
      document.getElementById('step2A').style.display = 'block';
      currentStep = 1;
    }
    
    updateModalTitle(currentStep);
    updateButtons(currentStep);
  }

  // Exponer las funciones para que sean accesibles desde los atributos onclick en el HTML
  window.nextStep = nextStep;
  window.previousStep = previousStep;

  /* Evento para la selección de un horario */
  document.addEventListener('click', function (event) {
    if (event.target.classList.contains('time-btn')) {
      document.querySelectorAll('.time-btn').forEach(btn => btn.classList.remove('selected'));
      event.target.classList.add('selected');

      const selectedDayBtn = document.querySelector('.day-btn.active');
      if (!selectedDayBtn) return;

      const parts = selectedDayBtn.dataset.date.split('-'); // Ejemplo: ["2025", "02", "18"]
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

      if (selectedDateTime.dateObject) {
        const day = selectedDateTime.dateObject.getDate().toString().padStart(2, '0');
        const month = (selectedDateTime.dateObject.getMonth() + 1).toString().padStart(2, '0');
        const year = selectedDateTime.dateObject.getFullYear();
        document.getElementById('hiddenDateField').value = `${year}-${month}-${day}`;
        document.getElementById('hiddenTimeField').value = selectedDateTime.time;
      }
    }

    if (selectedPsychologist) {
      document.getElementById('hiddenPsicologoField').value = selectedPsychologist;
    }
  });

  /* ------------------ Configuración del carrusel de días ------------------ */
  const daysShort = ['DOM', 'LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB'];
  const monthsShort = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];
  const fullDays = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
  const today = new Date();
  const dayOfWeek = today.getDay();
  const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
  const currentMonday = new Date(today);
  currentMonday.setDate(today.getDate() + mondayOffset);

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

      const daySpan = document.createElement('span');
      daySpan.classList.add('text-center');
      daySpan.textContent = dayShort;
      weekdaysContainer.appendChild(daySpan);

      const dayBtn = document.createElement('button');
      dayBtn.classList.add('day-btn', 'btn', 'btn-primary');
      dayBtn.innerHTML = `${dayNum}<br>${monthName}`;
      dayBtn.dataset.day = fullDay;
      const day = dateObj.getDate().toString().padStart(2, '0');
      const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
      const year = dateObj.getFullYear();
      dayBtn.dataset.date = `${year}-${month}-${day}`;

      dayBtn.addEventListener('click', function () {
        document.querySelectorAll('.day-btn').forEach(b => b.classList.remove('active', 'btn-primary'));
        this.classList.add('active', 'btn-primary');
        filterHorarios(this.dataset.day, this.dataset.date);
      });

      weekdatesContainer.appendChild(dayBtn);
    });
  }

  renderWeek(currentWeek, 'weekdays-current', 'weekdates-current');
  renderWeek(nextWeek, 'weekdays-next', 'weekdates-next');

  function filterHorarios(selectedDay, selectedDateString) {
    const activePsicologo = document.querySelector('#horarioSection .psicologo:not([style*="display: none"])');
    if (!activePsicologo) return;

    activePsicologo.querySelectorAll('.horario-container').forEach(container => {
      container.style.display = container.dataset.day === selectedDay ? 'block' : 'none';
      if (container.style.display === 'block') {
        const [year, month, day] = selectedDateString.split('-');
        const selectedDate = new Date(year, month - 1, day);
        const today = new Date();

        if (today.toDateString() === selectedDate.toDateString()) {
          container.querySelectorAll('.time-btn').forEach(timeBtn => {
            const timeText = timeBtn.textContent.trim();
            const [hour, minute] = timeText.split(':');
            const buttonTime = new Date(
              selectedDate.getFullYear(),
              selectedDate.getMonth(),
              selectedDate.getDate(),
              parseInt(hour, 10),
              parseInt(minute, 10)
            );
            if (buttonTime < today) {
              timeBtn.style.display = 'none';
            } else {
              timeBtn.style.display = 'inline-block';
            }
          });
        } else {
          container.querySelectorAll('.time-btn').forEach(timeBtn => {
            timeBtn.style.display = 'inline-block';
          });
        }
      }
    });
  }

  document.getElementById('horasModal').addEventListener('show.bs.modal', function (event) {
    currentStep = 1;
    selectedDateTime = {};
    updateModalTitle(1);
    updateButtons(1);
    document.getElementById('step1').style.display = 'block';
    document.getElementById('step2A').style.display = 'none';
    document.getElementById('step2').style.display = 'none';
    document.getElementById('confirmation').style.display = 'none';
    document.getElementById('selectedDateTimeText').textContent = '';
    document.getElementById('selectedTimeDisplay').style.display = 'none';
    document.querySelectorAll('.day-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.time-btn').forEach(btn => btn.classList.remove('selected'));

    const button = event.relatedTarget;
    selectedPsychologist = button.getAttribute('data-psicologo');
    selectedPsycholoid = button.getAttribute('data-psicologo-id');
    selectedSpecialty = button.getAttribute('data-especialidad') || '';

    document.querySelectorAll('#horarioSection .psicologo').forEach(el => {
      el.style.display = 'none';
    });

    const target = document.querySelector(`#horarioSection .psicologo[data-psicologo="${selectedPsychologist}"]`);
    if (target) {
      target.style.display = 'block';
      const availableDays = target.dataset.diasDisponibles.split(',');
      document.querySelectorAll('.day-btn').forEach(btn => {
        const [y, m, d] = btn.dataset.date.split('-');
        const buttonDate = new Date(y, m - 1, d);
        const isAvailable = availableDays.includes(btn.dataset.day);
        const todayStart = new Date();
        todayStart.setHours(0, 0, 0, 0);
        const isNotPast = buttonDate >= todayStart;
        btn.disabled = !(isAvailable && isNotPast);
        btn.classList.toggle('btn-primary', isAvailable && isNotPast);
        btn.classList.toggle('btn-secondary', !(isAvailable && isNotPast));
      });

      const todayName = fullDays[today.getDay()];
      const todayString = [
        today.getFullYear(),
        String(today.getMonth() + 1).padStart(2, '0'),
        String(today.getDate()).padStart(2, '0')
      ].join('-');

      filterHorarios(todayName, todayString);
    }
  });
});
