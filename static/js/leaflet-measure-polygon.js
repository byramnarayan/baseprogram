/*!
 * Leaflet Measure Polygon Control
 * A Leaflet control to measure area and perimeter of polygons
 * Requires Leaflet, Leaflet.draw, Leaflet.Editable, and Leaflet-measure-path
 */

L.Control.MeasurePolygon = L.Control.extend({
    options: {
        position: 'topleft',
        icon_active: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMyAzTDIxIDIxTTMgMjFMMjEgM00xMiAxMkwxOCA2TTE4IDE4TDYgNiIgc3Ryb2tlPSIjMzE2OTRFIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPjwvc3ZnPg==',
        icon_inactive: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMyA4SDIxTTggM1YyMU0xNiAzVjIxTTMgMTZIMjEiIHN0cm9rZT0iIzMxNjk0RSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz48L3N2Zz4=',
        html_template: '<div><p><b>Area:</b> _p_area</p><p><b>Perimeter:</b> _p_perimetro</p></div>',
        height: 130,
        width: 150,
        color_polygon: 'black',
        fillColor_polygon: 'yellow',
        weight_polygon: '2',
        msj_disable_tool: '¿Desea desabilitar la herramienta?'
    },

    onAdd: function (map) {
        this._map = map;
        this._active = false;
        this._polygon = null;

        const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');

        this._button = L.DomUtil.create('a', 'leaflet-bar-part', container);
        this._button.href = '#';
        this._button.title = 'Measure polygon area';
        this._button.style.width = '30px';
        this._button.style.height = '30px';
        this._button.style.display = 'flex';
        this._button.style.alignItems = 'center';
        this._button.style.justifyContent = 'center';
        this._button.innerHTML = '<img src="' + this.options.icon_inactive + '" width="20" height="20" />';

        L.DomEvent.on(this._button, 'click', this._toggleMeasure, this);
        L.DomEvent.disableClickPropagation(container);

        return container;
    },

    _toggleMeasure: function (e) {
        L.DomEvent.preventDefault(e);

        if (this._active) {
            this._deactivate();
        } else {
            this._activate();
        }
    },

    _activate: function () {
        this._active = true;
        this._button.innerHTML = '<img src="' + this.options.icon_active + '" width="20" height="20" />';
        this._button.style.backgroundColor = '#BBC863';

        this._map.doubleClickZoom.disable();

        // Start editing
        this._polygon = this._map.editTools.startPolygon(null, {
            color: this.options.color_polygon,
            fillColor: this.options.fillColor_polygon,
            weight: this.options.weight_polygon,
            showMeasurements: true,
            measurementOptions: {
                showArea: true,
                showLengths: true
            }
        });

        this._map.on('editable:drawing:end', this._onDrawEnd, this);
    },

    _deactivate: function () {
        if (confirm(this.options.msj_disable_tool)) {
            this._active = false;
            this._button.innerHTML = '<img src="' + this.options.icon_inactive + '" width="20" height="20" />';
            this._button.style.backgroundColor = '';

            if (this._polygon) {
                this._map.removeLayer(this._polygon);
                this._polygon = null;
            }

            if (this._resultDiv) {
                this._map.removeControl(this._resultControl);
                this._resultDiv = null;
            }

            this._map.editTools.stopDrawing();
            this._map.doubleClickZoom.enable();
            this._map.off('editable:drawing:end', this._onDrawEnd, this);
        }
    },

    _onDrawEnd: function (e) {
        const layer = e.layer;

        // Calculate area using Turf or simple calculation
        const area = L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]);
        const perimeter = this._calculatePerimeter(layer.getLatLngs()[0]);

        // Convert to appropriate units
        const areaHa = (area / 10000).toFixed(4);
        const areaText = areaHa + ' ha (' + (area / 1000000).toFixed(4) + ' km²)';
        const perimeterKm = (perimeter / 1000).toFixed(4) + ' km';

        // Show results
        this._showResults(areaText, perimeterKm);

        // Fire event with measurements
        this._map.fire('measurepolygon:measured', {
            layer: layer,
            area: area,
            perimeter: perimeter
        });
    },

    _calculatePerimeter: function (latlngs) {
        let perimeter = 0;
        for (let i = 0; i < latlngs.length; i++) {
            const p1 = latlngs[i];
            const p2 = latlngs[(i + 1) % latlngs.length];
            perimeter += p1.distanceTo(p2);
        }
        return perimeter;
    },

    _showResults: function (area, perimeter) {
        if (this._resultDiv) {
            this._map.removeControl(this._resultControl);
        }

        const ResultControl = L.Control.extend({
            options: {
                position: 'bottomleft'
            },
            onAdd: function () {
                const div = L.DomUtil.create('div', 'leaflet-measure-result');
                div.style.background = 'white';
                div.style.padding = '10px';
                div.style.borderRadius = '8px';
                div.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';
                div.style.minWidth = this.options.width + 'px';
                div.style.minHeight = this.options.height + 'px';

                const html = this.options.html_template
                    .replace('_p_area', area)
                    .replace('_p_perimetro', perimeter);

                div.innerHTML = html;
                return div;
            }
        });

        this._resultControl = new ResultControl({
            width: this.options.width,
            height: this.options.height,
            html_template: this.options.html_template
        });

        this._resultControl.addTo(this._map);
        this._resultDiv = true;
    },

    onRemove: function () {
        L.DomEvent.off(this._button, 'click', this._toggleMeasure, this);
    }
});

L.control.measurePolygon = function (options) {
    return new L.Control.MeasurePolygon(options);
};

// Polyfill for L.GeometryUtil.geodesicArea if not available
if (!L.GeometryUtil || !L.GeometryUtil.geodesicArea) {
    L.GeometryUtil = L.GeometryUtil || {};
    L.GeometryUtil.geodesicArea = function (latLngs) {
        const R = 6371000; // Earth's radius in meters
        let area = 0;
        const len = latLngs.length;

        if (len < 3) return 0;

        for (let i = 0; i < len; i++) {
            const p1 = latLngs[i];
            const p2 = latLngs[(i + 1) % len];
            area += (p2.lng - p1.lng) * (2 + Math.sin(p1.lat * Math.PI / 180) + Math.sin(p2.lat * Math.PI / 180));
        }

        area = Math.abs(area * R * R / 2.0);
        return area;
    };
}
