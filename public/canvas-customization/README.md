# bCourses customizations

In order to apply the bCourses skin and bCourses customizations, go to the Theme Editor within the Account Administration space.

Configure the following values:

## Global Branding

| Property              | Value   |
|-----------------------|---------|
| Primary Brand Color   | #002676 |
| Main Text Color       | #000000 |
| Link Color            | #004AAE |
| Primary Button        | #004AAE |
| Primary Button Text   | #FFFFFF |
| Secondary Button      | #FFC31B |
| Secondary Button Text | #002676 |

## Global Navigation

| Property              | Value                                                                             |
|-----------------------|-----------------------------------------------------------------------------------|
| Nav Background        | #002676                                                                           |
| Nav Icon              | #FFFFFF                                                                           |
| Nav Icon Active       | #002676                                                                           |
| Nav Text              | #FFFFFF                                                                           |
| Nav Text Active       | #002676                                                                           |
| Nav Avatar Border     | #FFFFFF                                                                           |
| Nav Badge             | #FFFFFF                                                                           |
| Nav Badge Active      | #002676                                                                           |
| Nav Badge Text        | #002676                                                                           |
| Nav Badge Text Active | #FFFFFF                                                                           |
| Nav Logo Background   | #002676                                                                           |
| Nav Logo              | [bcourses_lefthand.png](public/canvas-customization/images/bcourses_lefthand.png) |

## Watermarks & Other Images

| Property               | Value                                                                                         |
|------------------------|-----------------------------------------------------------------------------------------------|
| Watermark              | N/A                                                                                           |
| Watermark Opacity      | 100%                                                                                          |
| Favicon                | [favicon.ico](public/canvas-customization/images/favicon.ico)                                 |
| Mobile Homescreen Icon | [bcourses_ios_icon.png](public/canvas-customization/images/bcourses_ios_icon.png)             |
| Windows Tile Color     | #002676                                                                                       |
| Windows Tile: Square   | [bcourses_windows_square.png](public/canvas-customization/images/bcourses_windows_square.png) |
| Windows Tile: Wide     | [bcourses_windows_wide.png](public/canvas-customization/images/bcourses_windows_wide.png)     |
| Right Sidebar Logo     | [bcourses_righthand.png](public/canvas-customization/images/bcourses_righthand.png)           |

## Upload

| Property               | Value                                                           |
|----------------------- |-----------------------------------------------------------------|
| JavaScript file        | [index.js](public/canvas-customization/canvas-customization.js) |

**NOTE:** The `index.js` file will by default load resources from and make API requests to Ripley production. In order to point to a different Ripley server, the `window.RIPLEY` property in the `index.js` file should be updated to point to that server.
