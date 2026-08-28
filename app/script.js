let session;

async function loadModel(){
    session=await ort.InferenceSession.create("./model/model.onnx");
    console.log("Model loaded");
}