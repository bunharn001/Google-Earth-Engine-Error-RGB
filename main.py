// Define the area of interest (geometry) – replace with your actual geometry (polygon/rectangle).

Map.centerObject(geometry, 12);

// Function to mask clouds from Sentinel-2 imagery
function maskS2clouds(image) {
  var qa = image.select('QA60');

  // Bits 10 and 11 are clouds and cirrus, respectively.
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;

  // Both flags should be set to zero, indicating clear conditions.
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
      .and(qa.bitwiseAnd(cirrusBitMask).eq(0));

  return image.updateMask(mask).divide(10000);
}

// Sentinel-2 ImageCollection with band selection and cloud masking
var dataset = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                  .filterDate('2017-01-01', '2020-01-30')
                  .filterBounds(geometry)
                  // Pre-filter to get less cloudy granules
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 1))
                  .map(maskS2clouds)
                  .select(['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12', 'AOT', 'WVP', 'SCL', 'TCI_R', 'TCI_G', 'TCI_B']); // Select only the required bands

// Compute the median of the image collection (a composite image)
var expImg = dataset.median();

// DEM ImageCollection (COPERNICUS DEM)
var demdata = ee.ImageCollection("COPERNICUS/DEM/GLO30")
              .select('DEM') // Select only the DEM band
              .filterBounds(geometry);

// Visualization parameters for DEM and RGB
var elevationVis = {
  min: 0.0,
  max: 1000.0,
  palette: ['0000ff', '00ffff', 'ffff00', 'ff0000', 'ffffff'],
};

var visualization = {
  min: 0.0,
  max: 0.3,
  bands: ['B4', 'B3', 'B2'], // RGB bands for Sentinel-2 imagery
};

// Add the DEM layer and RGB composite to the map
Map.addLayer(demdata.mean(), elevationVis, 'DEM');
Map.addLayer(expImg, visualization, 'RGB');

// Export the Sentinel-2 RGB composite to Google Drive
Export.image.toDrive({
  image: expImg.select(["B4", "B3", "B2"]), // RGB bands
  description: 'Faroe_Sentinel2_RGB',
  folder: 'ee_demos',
  region: geometry,
  scale: 30,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

// Export the DEM to Google Drive
Export.image.toDrive({
  image: demdata.mean(),
  description: 'Faroe_DEM',
  folder: 'ee_demos',
  region: geometry,
  scale: 30,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});
