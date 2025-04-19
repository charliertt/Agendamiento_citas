document.addEventListener('DOMContentLoaded', function() {


    const commonConfig = {
        expandRows: true,
        dayMinWidth: 220,
        eventMinHeight: 110,
        slotMinTime: '08:00',
        slotMaxTime: '20:00',
        slotDuration: '01:00',
        themeSystem: 'bootstrap5',
        locale: 'es',
        timeZone: 'America/Bogota',
        dayHeaderFormat: { weekday: 'short', day: 'numeric' },
        fixedWeekCount: false,
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
        timeZone: 'America/Bogota', // Cambiado de 'UTC' a 'America/Bogota'
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
        
        events: contactosData.map(contacto => {
            // Paso 1: Capturar la fecha original del backend
            const fechaOriginal = contacto.fecha_creacion;
            
            // Paso 2: Eliminar la parte horaria (si existe)
            const fechaSolo = fechaOriginal.includes('T') 
                ? fechaOriginal.split('T')[0] 
                : fechaOriginal.split(' ')[0]; // Soporta formatos "YYYY-MM-DD HH:mm:ss"

            // Paso 3: Forzar la fecha en zona horaria de Bogotá
            const fechaBogota = new Date(
                fechaOriginal.replace('T', ' ') + ' UTC' // Fuerza a JS a interpretar la fecha como UTC
            );
            fechaBogota.setHours(12)

            
            // Depuración
            console.log('[Contactos] Procesando:', {
                id: contacto.id,
                fecha_original: fechaOriginal,
                fecha_solo: fechaSolo,
                fechaBogota: fechaBogota.toISOString()
            });

            return {
                title: `${contacto.nombre} - ${getDeseoDisplay(contacto.deseo)}`,
                start: fechaBogota, // Usar Date ajustado
                color: getColorByType(contacto.deseo),
                allDay: true
            };
        }),
        eventDidMount: function(info) { // Depuración de renderizado
            console.log('[Contactos] Evento renderizado:', {
                title: info.event.title,
                start: info.event.start.toISOString(),
                start_local: info.event.start.toLocaleString('es-CO', {
                    timeZone: 'America/Bogota'
                })
            });
        }
    });
    contactosCalendar.render();
    


    
    
    

    // Calendario de Citas
    const citasData = JSON.parse(document.getElementById('citas-data').textContent);

    citasData.forEach(cita => {
        console.log('Datos de cita recibidos:', {
            nombre: cita.nombre_completo,
            fecha_hora: cita.fecha_hora,
            fecha_parseada: new Date(cita.fecha_hora).toLocaleString('es-CO', {
                timeZone: 'America/Bogota'
            })
        });
    });

    const calendarCitasEl = document.getElementById('calendar_citas');
    
    const citasCalendar = new FullCalendar.Calendar(calendarCitasEl, {
        // Configuración existente
        locale: 'es',
        timeZone: 'local',
        firstDay: 1,
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'timeGridWeek,timeGridDay,listWeek'
        },
        buttonText: {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día',
            list: 'Lista'
        },

        
        
        // Ajustes para corregir la visualización
        slotDuration: '01:00:00',
        slotEventOverlap: false,
        height: 'auto',                // Permite que el calendario se expanda según se necesite
        contentHeight: 'auto',         // Altura automática del contenido
        aspectRatio: 2.5,              // Relación ancho/alto (ajusta según necesites)
        allDaySlot: false,             // Quitar la fila "todo el día" si no se usa
        slotMinTime: '07:00:00',       // Hora mínima visible
        slotMaxTime: '20:00:00',       // Hora máxima visible
        
        // Formato de hora
        eventTimeFormat: { 
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
            meridiem: 'short'
        },
        events: citasData.map(cita => {
            // Extraer la fecha y hora de la cadena ISO
            const fechaHoraOriginal = cita.fecha_hora;
            const [fecha, horaConOffset] = fechaHoraOriginal.split('T');
            const [hora, min, segConOffset] = horaConOffset.split(':');
            
            // Crear objeto Date explícitamente con los componentes extraídos
            const year = parseInt(fecha.split('-')[0]);
            const month = parseInt(fecha.split('-')[1]) - 1; // Meses en JS son 0-indexed
            const day = parseInt(fecha.split('-')[2]);
            const hours = parseInt(hora);
            const minutes = parseInt(min);
            
            // Crear fechas de inicio y fin explícitamente
            const startDate = new Date(year, month, day, hours, minutes, 0);
            const endDate = new Date(year, month, day, hours + 1, minutes, 0);
            
            console.log('Procesando cita con fechas explícitas:', {
                nombre: cita.nombre_completo,
                fecha_original: fechaHoraOriginal,
                componentes: {fecha, hora, min, year, month, day, hours, minutes},
                startDate_local: startDate.toLocaleString('es-CO'),
                endDate_local: endDate.toLocaleString('es-CO')
            });
            
            return {
                title: `${cita.asunto} - ${cita.nombre_completo}`,
                start: startDate,  // Usar objeto Date directamente
                end: endDate,      // Usar objeto Date directamente
                color: getCitaColor(cita.estado),
                extendedProps: {
                    estado: cita.estado.toLowerCase(),
                    horaOriginal: hours // Guardamos la hora original para debugging
                }
            };
        }),
        
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
                <div class="d-flex flex-column">
                    <div class="fw-bold" style="font-size: 0.95em">
                        ${nombre} - ${tipo}
                    </div>
                  
                    <div class="text-primary" style="font-size: 0.75em">
                        ${formatDate(eventInfo.event.start)}
                    </div>
                </div>
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