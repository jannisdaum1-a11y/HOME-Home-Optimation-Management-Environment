import './DragAndDrop.css';
import assets from './assets/assets.json'

/** Initialize Counter for naming of objects */
const counter: Record<string,number> = {}
Object.keys(assets).forEach(element => {
    counter[element]=0;
});
type Asset = {
    image: string;
    [key: string]: unknown;
};


function DisplayObject({object}: {object:Asset}) {
    return (
        <>
        <img src={object.image} alt={String(object.name)}></img>
        <p>{object.name}</p>
        </>
    )
}



type DragAndDropProps = {
    objects: Asset[];
    setObjects: React.Dispatch<React.SetStateAction<Asset[]>>;
    setSelectedObject: React.Dispatch<React.SetStateAction<Asset|null>>;
};
function DragAndDrop({objects, setObjects, setSelectedObject}: DragAndDropProps){

    function handleDrop(e) {
    e.preventDefault();
    const object = e.dataTransfer.getData("asset");
    const data: Asset = structuredClone(assets[object]);

    /**Check for default value */
    for (const [key, value] of Object.entries(data)) {
        const default_value = objects[0][key] ?? false;

        if (!value && default_value) {
            data[key] = default_value;
        }
    }

    data.name = data.name + "_" + counter[object]++;
    setObjects(prev => [...prev, data]);
    console.log(objects);
    }

    function handleDelete(objectName: unknown) {
        setObjects(prev => prev.filter(object => object.name !== objectName));
        setSelectedObject(prev => prev && prev.name === objectName ? null : prev);
    }


    return (
        <div className='DragAndDrop' 
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}>
            {
                objects.length===0 && (<p>Ziehen Sie die gewünschten Elemente in den unteren Bereich</p>)
            }
            {
                objects.map((element) => (
                    !(element.name==="config") &&
                    <div className='DisplayObject'
                     key={element.name}
                     onClick={() => setSelectedObject(element)}>
                        <DisplayObject object={element}></DisplayObject>
                        <button
                            type='button'
                            className='DeleteObject'
                            aria-label={`${String(element.name)} löschen`}
                            onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(element.name);
                            }}
                        >
                            Löschen
                        </button>
                    </div>
                )
            )
            }
        </div>
    );
}

export default DragAndDrop