window.onload = function () {
  window.ui = SwaggerUIBundle({
    url: "https://petstore.swagger.io/v2/swagger.json",
    dom_id: "#swagger-ui",
    configUrl: "swagger-config.json",
  });
};
