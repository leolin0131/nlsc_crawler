;"use strict";
/**
 * 球面墨卡托。
 *
 * @const {ol.proj.Projection}
 */
qt.map.PROJ_3857 = new ol.proj.get("EPSG:3857");

/**
 * WGS84。
 *
 * @const {ol.proj.Projection}
 */
qt.map.PROJ_4326 = new ol.proj.get("EPSG:4326");



/*==================================================*/

/**
 * 清空圖層。
 *
 * @param {ol.layer.Vector} layer
 * @param {string} key 僅刪除含有特定屬性的圖元。
 * @param {string} [value] 僅刪除特定屬性值的圖元。
 */
qt.map.clrLayer = function(layer, key, value) {
	if(!layer || !(layer instanceof ol.layer.Vector)) {
		console.log("請指定layer");
		return;
	}
	
	var source = layer.getSource();
	if(qt.util.hasEmpty(key)) {
		source.clear();
	} else {
		var target = [];
		var chkValue = !qt.util.hasEmpty(value);
		source.forEachFeature(function(feature) {
			var attrValue = feature.get(key);
			if(attrValue 
					&& (!chkValue || (chkValue && opt.value === attrValue))) {
				target.push(feature);
			}
			return false; // continue
		});
		if(target.length > 0) {
			for(var i = 0, len = target.length; i < len; i++) {
				source.removeFeature(target[i]);
			}
		}
	}
};

/**
 * 移除圖層。
 * 
 * @param {ol.Map} map
 * @param {string} key 僅移除含有特定屬性的圖層。
 * @param {string} [value] 僅移除特定屬性值的圖層。
 */
qt.map.rmLayer = function(map, key, value) {
	if(!map || !(map instanceof ol.Map)) {
		console.log("請指定map");
		return;
	}
	var layers = map.getLayers();
	if(!layers && layers.get("length") <= 0) {
		return;
	}
	
	var target = [];
	var chkValue = !qt.util.hasEmpty(value);
	layers.forEach(function(layer) {
		var attrValue = layer.get(key);
		if(attrValue 
				&& (!chkValue || (chkValue && value === attrValue))) {
			target.push(layer);
		}
	});
	if(target.length > 0) {
		for(var i = 0, len = target.length; i < len; i++) {
			map.removeLayer(target[i]);
		}
	}
};

/**
 * 地圖是否含有控件。
 * 
 * @param {ol.Map} map
 * @param {ol.control.Control} ctrl
 * @return {boolean} true，含有。
 */
qt.map.hasCtrl = function(map, ctrl) {
	var result = false;
	if(!map || !(map instanceof ol.Map) || !ctrl || !(ctrl instanceof ol.control.Control)) {
		console.log("請指定map、ctrl");
		return false;
	}
	var ctrls = map.getControls();
	ctrls.forEach(function(c) {
		if(ctrl === c) {
			result = true;
		}
	});
	return result;
};

/**
 * 地圖新增控件。
 * 
 * @param {ol.Map} map
 * @param {ol.control.Control} ctrl
 */
qt.map.addCtrl = function(map, ctrl) {
	if(!map || !(map instanceof ol.Map) || !ctrl || !(ctrl instanceof ol.control.Control)) {
		console.log("請指定map、ctrl");
		return;
	}
	if(qt.map.hasCtrl(map, ctrl)) {
		return;
	}
	map.addControl(ctrl);
};

/**
 * 地圖是否含有互動。
 * 
 * @param {ol.Map} map
 * @param {ol.interaction.Interaction} iact
 * @return {boolean} true，含有。
 */
qt.map.hasIact = function(map, iact) {
	var result = false;
	if(!map || !(map instanceof ol.Map) || !iact || !(iact instanceof ol.interaction.Interaction)) {
		console.log("請指定map、iact");
		return;
	}
	var iacts = map.getInteractions();
	iacts.forEach(function(c) {
		if(iact === c) {
			result = true;
		}
	});
	return result;
};

/**
 * 地圖新增互動。
 * 
 * @param {ol.Map} map
 * @param {ol.interaction.Interaction} iact
 */
qt.map.addIact = function(map, iact) {
	if(!map || !(map instanceof ol.Map) || !iact || !(iact instanceof ol.interaction.Interaction)) {
		console.log("請指定map、iact");
		return;
	}
	if(qt.map.hasIact(map, iact)) {
		return;
	}
	map.addInteraction(iact);
}

/**
 * 獲取圖層預設樣式。
 * 
 * @param {ol.Feature} feature
 * @param {number} resolution
 * @return {Array.<ol.style.Style>}
 */
qt.map.getDefStyle = function(feature, resolution) {
	var fill = new ol.style.Fill({
		color : "rgba(255,255,255,0.4)"
	});
	var stroke = new ol.style.Stroke({
		color : "#3399CC",
		width : 1.25
	});
	var style = [
		new ol.style.Style({
			image : new ol.style.Circle({
				fill : fill,
				stroke : stroke,
				radius : 5
			}),
			fill : fill,
			stroke : stroke
		})
	];
	return style;
};

/**
 * 獲取ol.interaction.Select預設樣式。
 * 
 * @param {ol.Feature} feature
 * @param {number} resolution
 * @return {?Array.<ol.style.Style>}
 */
qt.map.getDefSelStyle = function(feature, resolution) {
	var styles = qt.map.creDefEditStyle();
	styles["Polygon"] = styles["Polygon"].concat(styles["LineString"]);
	if (!feature.getGeometry()) {
		return null;
	}
	return styles[feature.getGeometry().getType()];
};

/**
 * 建立圖層預設樣式(編輯模式)。
 * 
 * @return {Object.<ol.geom.GeometryType, Array.<ol.style.Style>>}
 */
qt.map.creDefEditStyle = function() {
	var styles = {};
	var white = [ 255, 255, 255, 1 ];
	var blue = [ 0, 153, 255, 1 ];
	var width = 3;
	
	styles["Polygon"] = [
		new ol.style.Style({
			fill : new ol.style.Fill({
				color : [ 255, 255, 255, 0.5 ]
			})
		})
	];
	styles["MultiPolygon"] = styles["Polygon"];

	styles["LineString"] = [
		new ol.style.Style({
			stroke : new ol.style.Stroke({
				color : white,
				width : width + 2
			})
		}),
		new ol.style.Style({
			stroke : new ol.style.Stroke({
				color : blue,
				width : width
			})
		})
	];
	styles["MultiLineString"] = styles["LineString"];

	styles["Circle"] = styles["Polygon"].concat(styles["LineString"]);

	styles["Point"] = [
		new ol.style.Style({
			image : new ol.style.Circle({
				radius : width * 2,
				fill : new ol.style.Fill({
					color : blue
				}),
				stroke : new ol.style.Stroke({
					color : white,
					width : width / 2
				})
			}),
			zIndex : Infinity
		})
	];
	styles["MultiPoint"] = styles["Point"];

	styles["GeometryCollection"] = styles["Polygon"].concat(styles["LineString"], styles["Point"]);

	return styles;
};
