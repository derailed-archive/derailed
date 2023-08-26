use bitflags::bitflags;


// For anyone sneaking around here:
// https://docs.rs/bitflags/2.3.3/bitflags/example_generated/struct.Flags.html


bitflags! {
    #[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
    pub struct UserFlags: u64 {
        const STAFF = 1 << 0;
        const ADMIN = 1 << 1;
        const VERIFIED = 1 << 2;
        const EARLY_SUPPORTER = 1 << 3;
        const VERIFIED_EMAIL =  1 << 4;
    }
}

impl UserFlags {
    pub fn default() -> Self {
        let mut ret = Self::empty();
        ret.toggle(Self::EARLY_SUPPORTER);
        return ret;
    }

    pub fn clear(&mut self) {
        *self.0.bits_mut() = 0;
    }
}
