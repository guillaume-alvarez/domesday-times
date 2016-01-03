/*
 * A Camera object that can be used to maintain a viewport container.
 */
var Camera = function() {
    this.x = Number.MAX_SAFE_INTEGER;
    this.y = Number.MAX_SAFE_INTEGER;
    this.width = 0;
    this.height = 0;
    this.scale = 1.0;
};

Camera.prototype.include = function(x, y) {
    if (x < this.x) this.x = x;
    else if (x - this.x > this.width) this.width = x - this.x;
    if (y < this.y) this.y = y;
    else if (y - this.y > this.height) this.height = y - this.y;
};

var BORDER = 20;

Camera.prototype.init = function(renderer, viewport, stage) {
    this.renderer = renderer;
    this.viewport = viewport;
    this.stage = stage;

    // compute scale so that all the scene is in the screen
    scaleX = (this.renderer.width - BORDER * 2) / this.width;
    scaleY = (this.renderer.height - BORDER * 2) / this.height;
    this.scale = Math.min(scaleX, scaleY);

    this.apply();
};

Camera.prototype.zoom = function(delta) {
    this.scale += this.scale * delta;
    this.apply();
    this.renderer.render(stage);
};

Camera.prototype.apply = function() {
    this.viewport.scale.x = this.scale;
    this.viewport.scale.y = this.scale;
    this.viewport.position.x = -this.x * this.scale + BORDER;
    this.viewport.position.y = -this.y * this.scale + BORDER;

    this.renderer.render(stage);
};