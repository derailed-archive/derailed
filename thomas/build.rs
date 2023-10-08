fn main() {
    tonic_build::compile_protos("../protos/thomas.proto").unwrap();
}
