document.addEventListener('DOMContentLoaded', function() {


    const commonConfig = {
        expandRows: true,
        dayMinWidth: 150,
        eventMinHeight: 70,
        slotMinTime: '08:00',
        slotMaxTime: '20:00',
        slotDuration: '01:00',
        themeSystem: 'bootstrap5',
        locale: 'es',
        timeZone: 'America/Bogota',
        firstDay: 1,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
        },
        buttonText: {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día',
            list: 'Lista'
        }
    };
    // Calendario de Contactos
    const contactosData = JSON.parse(document.getElementById('contactos-data').textContent);
    const calendarEl = document.getElementById('calendar');

    
    const contactosCalendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'es',
        timeZone: 'UTC',
        firstDay: 1,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
        },
        buttonText: {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día',
            list: 'Lista'
        },
        events: contactosData.map(contacto => ({
            title: `${contacto.nombre} - ${getDeseoDisplay(contacto.deseo)}`,
            start: contacto.fecha_creacion,
            color: getColorByType(contacto.deseo),
            allDay: true
        })),
        themeSystem: 'bootstrap5',
        eventContent: renderContactoContent // Nueva función de renderizado
    });
    contactosCalendar.render();

    // Calendario de Citas
    const citasData = JSON.parse(document.getElementById('citas-data').textContent);
    const calendarCitasEl = document.getElementById('calendar_citas');
    
    const citasCalendar = new FullCalendar.Calendar(calendarCitasEl, {
        locale: 'es',
        timeZone: 'America/Bogota',
        firstDay: 1,
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next Hoy',
            center: 'title',
            right: 'timeGridWeek,timeGridDay,listWeek'
        },
        events: citasData.map(cita => ({
            title: `${cita.asunto} - ${cita.nombre_completo}`,
            start: cita.fecha_hora,
            
            color: getCitaColor(cita.estado),
            extendedProps: {
                estado: cita.estado.toLowerCase() 
            }
        })),
        eventContent: renderCitaContent,
        themeSystem: 'bootstrap5',
        eventTimeFormat: { 
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
            meridiem: 'short' // Muestra AM/PM
        },
        slotLabelFormat: {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
            meridiem: 'short'
        }
        
    });
    citasCalendar.render();
});

// Funciones para Contactos
function renderContactoContent(eventInfo) {
    return {
        html: `
            <div class="contacto-event">
                <div class="fw-bold small">${eventInfo.event.title}</div>
                <div class="text-muted x-small">${formatDate(eventInfo.event.start)}</div>
            </div>
        `
    };
}

function getDeseoDisplay(deseo) {
    const opciones = {
        'queja': 'Queja',
        'reclamo': 'Reclamo',
        'peticion': 'Petición'
    };
    return opciones[deseo] || 'Solicitud';
}0

function getColorByType(tipo) {
    switch(tipo) {
        case 'queja': return '#dc3545';
        case 'reclamo': return '#ffc107';
        case 'peticion': return '#28a745';
        default: return '#17a2b8';
    }
}

// Funciones para Citas
function renderCitaContent(eventInfo) {
    const [asunto, estudiante] = eventInfo.event.title.split('-').map(s => s.trim());
    const borderColor = getCitaBorderColor(eventInfo.event.extendedProps.estado);
    
    return {
        html: `
           <div class="cita-event p-1" style="border: 2px solid ${borderColor};">
                <div class="d-flex flex-column gap-1">
                    <div class="event-header">
                        <div class="estudiante-text text-muted">
                            ${estudiante.replace(/(^\w{1})|(\s+\w{1})/g, letra => letra.toUpperCase())}
                        </div>
                    </div>

                     <div class="d-flex justify-content-between align-items-center">
                        <span class="badge badge-estado ${getEstadoBadgeClass(eventInfo.event.extendedProps.estado)}">
                            ${eventInfo.event.extendedProps.estado}
                        </span>

                    </div>
                    
                </div>
            </div>
        `
    };
}

function getCitaColor(estado) {
    switch(estado) {
        case 'agendada': return 'transparent';
        case 'cancelada': return 'transparent';
        case 'completada': return 'transparent';
        default: return '#17a2b8';
    }
}

function getEstadoBadgeClass(estado) {
    return {
        'agendada': 'badge badge-outline text-orange',  
        'cancelada': 'badge badge-outline text-red',
        'completada': 'badge badge-outline text-green'
    }[estado] || 'bg-warning text-dark';
}

// Función auxiliar para formato de fecha
function formatDate(date) {
    return new Date(date).toLocaleDateString('es-ES', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
}


function getCitaBorderColor(estado) {
    switch(estado) {
        case 'agendada': return '#e67f60';
        case 'cancelada': return '#dc3545';
        case 'completada': return '#17a2b8'; // o el color que prefieras
        default: return '#17a2b8';
    }
}