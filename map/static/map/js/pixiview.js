
//Create the renderer
var renderer = PIXI.autoDetectRenderer(256, 256);
renderer.backgroundColor = 0x061639;
renderer.view.style.position = "absolute";
renderer.view.style.display = "block";
renderer.autoResize = true;
// 10px for scroll bars and such
renderer.resize(window.innerWidth - 10, window.innerHeight - 10);

//Add the canvas to the HTML document
document.body.appendChild(renderer.view);

PIXI.loader
    .add("villageImage", villageImage)
    .add("placesJson", placesJson)

    .load(function (loader, resources) {
        var container = new PIXI.ParticleContainer();
        var texture = resources.villageImage.texture;
        var camera = new Camera();

        for (var i in resources.placesJson.data) {
            var sprite = new PIXI.Sprite(texture);
            var place = resources.placesJson.data[i];
            sprite.position.x = place.fields.longitude * texture.width * 100.0;
            // latitude is from south, Y is from screen top
            sprite.position.y = -place.fields.latitude * texture.height * 100.0;

            camera.include(sprite.position.x, sprite.position.y);
            container.addChild(sprite);
        }


        camera.init(renderer.width, renderer.height);
        camera.apply(container);
        renderer.render(container);
    });