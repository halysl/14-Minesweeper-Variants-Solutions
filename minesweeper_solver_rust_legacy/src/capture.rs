use image::DynamicImage;
use anyhow::Result;

/// Trait for capturing the screen or a specific window.
pub trait ScreenCapture {
    /// Captures the entire screen or the game window.
    fn capture(&self) -> Result<DynamicImage>;
}
