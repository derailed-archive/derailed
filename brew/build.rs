fn main() {
    tonic_build::compile_protos("../wsi.proto").unwrap();
}
