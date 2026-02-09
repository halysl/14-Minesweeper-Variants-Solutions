use anyhow::Result;

/// Trait for controlling the mouse and keyboard.
pub trait GameControl {
    /// Move mouse to (x, y)
    fn move_mouse(&self, x: i32, y: i32) -> Result<()>;
    
    /// Click left mouse button at current position
    fn left_click(&self) -> Result<()>;
    
    /// Click right mouse button at current position
    fn right_click(&self) -> Result<()>;
}
