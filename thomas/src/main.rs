mod grpc {
    tonic::include_proto!("derailed.thomas");
}
use grpc::JsonResult;
use mineral::{Track, DBTrack, User};
use std::collections::{BTreeMap, HashMap};
use tonic::{transport::Server, Request, Response, Status};
use mimalloc::MiMalloc;


#[global_allocator]
static GLOBAL: MiMalloc = MiMalloc;


#[derive(Debug)]
struct ThomasState {
    tracks: BTreeMap<i64, Track>,
    users: BTreeMap<i64, User>
}


fn db_to_track(db_track: DBTrack, reactions: HashMap<String, i64>) -> Track {
    Track {
        id: db_track.id,
        author_id: db_track.author_id,
        guild_id: db_track.author_id,
        origin_track_id: db_track.origin_track_id,
        r#type: db_track.r#type,
        content: db_track.content,
        reactions
    }
}


#[tonic::async_trait]
impl grpc::thomas_server::Thomas for ThomasState {
    async fn fetch_track(
        &self,
        request: tonic::Request<grpc::JustId>,
    ) -> Result<Response<JsonResult>, Status> {
        let track_id = request.into_inner().id;

        if let Some(track) = self.tracks.get(&track_id) {
            Ok(Response::new(JsonResult {result: serde_json::to_string(track).map_err(|_| Status::internal("Unable to encode JSON"))?}))
        } else {
            let session = mineral::acquire().await;

            let dbtrack = sqlx::query_as!(
                DBTrack,
                "SELECT * FROM tracks WHERE id = $1;",
                &track_id
            )
            .fetch_optional(session)
            .await
            .map_err(|_| Status::internal("Failed to fetch track from database"))?;

            if let Some(db_track) = dbtrack {
                // TODO: add reactions once they are implemented
                Ok(
                    Response::new(JsonResult { result: serde_json::to_string(&db_to_track(
                        db_track,
                        HashMap::new()
                    )).map_err(|_| Status::internal("Unable to encode JSON"))? })
                )
            } else {
                Ok(Response::new(JsonResult { result: "0".to_string() }))
            }
        }
    }
}


fn main() {
    println!("Hello, world!");
}
