# RideBody Map Tiles

## Overview

RideBody uses Leaflet for map rendering.

The tile provider is configurable through environment variables:

- `RIDE_MAP_TILE_URL`
- `RIDE_MAP_TILE_ATTRIBUTION`

This allows different tile providers to be used in development and production without changing the application code.

## Development

The application uses OpenStreetMap raster tiles:

```
https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

Attribution:

```
© OpenStreetMap contributors
```

## Production

The long-term production plan is to use custom Almaty-only raster tiles.

Planned characteristics:

- Almaty city only
- Zoom levels 10–17
- Tiles stored outside Git
- Tiles hosted on AWS S3
- Served through CloudFront
- Configured using environment variables

## Configuration

Example:

```
RIDE_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
RIDE_MAP_TILE_ATTRIBUTION=&copy; OpenStreetMap contributors
```
