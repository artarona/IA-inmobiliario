// filtros.js
export function obtenerFiltrosSeleccionados() {
    const filtros = {};
    const campos = [
        ['operacion', 'operacion'],
        ['barrio', 'neighborhood'],
        ['tipo', 'tipo'],
        ['ambientes', 'min_rooms'],
        ['precioMin', 'min_price'],
        ['precioMax', 'max_price'],
        ['metrosMin', 'min_sqm'],
        ['metrosMax', 'max_sqm']
    ];

    campos.forEach(([id, key]) => {
        const valor = document.getElementById(id).value;
        if (valor) filtros[key] = isNaN(valor) ? valor : parseFloat(valor);
    });

    return filtros;
}

export function limpiarFiltros() {
    ['operacion','barrio','tipo','ambientes','precioMin','precioMax','metrosMin','metrosMax']
        .forEach(id => document.getElementById(id).value = '');
}
