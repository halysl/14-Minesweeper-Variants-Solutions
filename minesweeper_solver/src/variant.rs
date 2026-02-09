/// Trait for different Minesweeper variants.
pub trait GameVariant {
    /// Returns the name of the variant.
    fn name(&self) -> &str;
    
    // Add more methods for variant-specific logic here
}
