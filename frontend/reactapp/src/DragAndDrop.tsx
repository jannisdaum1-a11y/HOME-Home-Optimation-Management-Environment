import './DragAndDrop.css';
type Asset = {
    image?: string;
    [key: string]: unknown;
};


function DisplayObject({object}: {object:Asset}) {
    return (
        <>
        <img src={object.image ?? ""} alt={String(object.name)}></img>
        <p>{String(object.name)}</p>
        </>
    )
}
type DragAndDropProps = {
    objects: Asset[];
    setObjects: React.Dispatch<React.SetStateAction<Asset[]>>;
    setSelectedObject: React.Dispatch<React.SetStateAction<Asset|null>>;
    draggedAsset: string | null;
    onPointerDrop: () => void;
};
function DragAndDrop({objects, setObjects, setSelectedObject, draggedAsset, onPointerDrop}: DragAndDropProps){

    function handleDelete(objectName: unknown) {
        setObjects(prev => prev.filter(object => object.name !== objectName));
        setSelectedObject(prev => prev && prev.name === objectName ? null : prev);
    }


    return (
        <div className='DragAndDrop' 
        onPointerUp={(event) => {
            event.preventDefault();
            if (draggedAsset) onPointerDrop();
        }}>
            {
                objects.length===0 && (<p>Ziehen Sie die gewünschten Elemente in den unteren Bereich</p>)
            }
            {
                objects.map((element) => (
                    !(element.name==="config") &&
                    <div className='DisplayObject'
                     key={String(element.name)}
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