fn main() {
    tonic_build::compile_protos("../protos/wsi.proto").unwrap();
}
